from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва курсу")
    description = models.TextField(verbose_name="Опис курсу")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses',
                               limit_choices_to={'is_staff': True}, verbose_name="Автор/Викладач", default=1)
    is_published = models.BooleanField(default=False, verbose_name="Статус публікації")

    def calculate_inclusivity_index(self):

        course_lessons = self.lessons.all()
        total_lessons = course_lessons.count()

        if total_lessons == 0:
            return 0.0

        w1, w2, w3 = 0.5, 0.3, 0.2

        v_tot = sum(lesson.video_duration for lesson in course_lessons)
        v_sub = sum(lesson.video_duration for lesson in course_lessons if lesson.subtitle_file)
        sub_ratio = (v_sub / v_tot) if v_tot > 0 else 0.0

        t_trans = course_lessons.filter(has_transcript=True).count()
        trans_ratio = t_trans / total_lessons

        a_tot = sum(lesson.total_alerts_count for lesson in course_lessons)
        a_vis = sum(lesson.visual_alerts_count for lesson in course_lessons)
        alert_ratio = (a_vis / a_tot) if a_tot > 0 else 1.0

        i_inc = (w1 * sub_ratio + w2 * trans_ratio + w3 * alert_ratio) * 100
        return round(i_inc, 2)

    def clean(self):

        if self.is_published:
            current_index = self.calculate_inclusivity_index()
            if current_index < 80.0:
                raise ValidationError(
                    f"Блокування транзакції бази даних! Поточний індекс інклюзивної доступності курсу становить {current_index}%, "
                    f"що нижче встановленого нормативного обмеження у 80%. Будь ласка, додайте текстові транскрипти або налаштуйте сповіщення."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="Курс")
    title = models.CharField(max_length=200, verbose_name="Назва лекції")
    video_file = models.FileField(upload_to='videos/', verbose_name="Відеофайл")
    video_duration = models.IntegerField(default=15, help_text="Тривалість відео у хвилинах (V_tot)",
                                         verbose_name="Тривалість відео (хв)")

    subtitle_file = models.FileField(upload_to='subtitles/', blank=False, null=False,
                                     verbose_name="Файл субтитрів (.vtt)")

    has_transcript = models.BooleanField(default=False, verbose_name="Наявність текстового транскрипту")
    transcript_text = models.TextField(blank=True, verbose_name="Текст конспекту лекції")

    total_alerts_count = models.IntegerField(default=5, verbose_name="Загальна кількість сповіщень подій (A_tot)")
    visual_alerts_count = models.IntegerField(default=5, verbose_name="Кількість візуалізованих сповіщень (A_vis)")

    def clean(self):
        if self.video_file and not self.subtitle_file:
            raise ValidationError("Помилка інклюзивності: до відео обов'язково має бути доданий файл субтитрів (.vtt)!")

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress', verbose_name="Студент")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress', verbose_name="Лекція")
    is_completed = models.BooleanField(default=False, verbose_name="Лекцію завершено")
    completed_at = models.DateTimeField(auto_now=True, verbose_name="Дата останньої активності")

    class Meta:
        verbose_name = "Прогрес лекції"
        verbose_name_plural = "Прогрес студентів"
        unique_together = ('user', 'lesson')

    def __str__(self):
        status = "✅" if self.is_completed else "❌"
        return f"{self.user.username} | {self.lesson.title} | {status}"


class LabSubmission(models.Model):

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='submissions', verbose_name="Курс")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lab_submissions', verbose_name="Студент")
    lab_title = models.CharField(max_length=200, verbose_name="Назва лабораторної роботи")
    file = models.FileField(upload_to='labs/', verbose_name="Файл виконаної роботи")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата завантаження")

    grade = models.IntegerField(null=True, blank=True, verbose_name="Оцінка (за 12-бальною шкалою)")
    teacher_comment = models.TextField(blank=True, verbose_name="Коментар викладача")
    is_checked = models.BooleanField(default=False, verbose_name="Статус перевірки")

    class Meta:
        verbose_name = "Лабораторна робота"
        verbose_name_plural = "Лабораторні роботи"

    def __str__(self):
        return f"{self.student.username} - {self.lab_title} ({self.course.title})"


class LabAssignment(models.Model):

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments', verbose_name="Курс")
    title = models.CharField(max_length=200, verbose_name="Назва завдання")
    description = models.TextField(verbose_name="Опис та інструкція")
    instruction_file = models.FileField(upload_to='instructions/', blank=True, null=True, verbose_name="Файл з методичкою")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Завдання до лабораторної"
        verbose_name_plural = "Завдання до лабораторних"

    def __str__(self):
        return f"{self.course.title} - {self.title}"
class SupportMessage(models.Model):

    user_name = models.CharField(max_length=100, verbose_name="Ім'я користувача")
    email = models.EmailField(verbose_name="Email для відповіді")
    message = models.TextField(verbose_name="Текст звернення")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата звернення")
    is_resolved = models.BooleanField(default=False, verbose_name="Опрацьовано")

    class Meta:
        verbose_name = "Звернення в підтримку"
        verbose_name_plural = "Звернення в підтримку"

    def __str__(self):
        return f"Звернення від {self.user_name} ({self.created_at.strftime('%d.%m.%Y')})"