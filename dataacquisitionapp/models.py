from django.db import models


# user.get?ID=1
class User(models.Model):
    ID = models.PositiveIntegerField(primary_key=True, verbose_name='ID пользователя в BX24', unique=True, db_index=True)
    LAST_NAME = models.CharField(verbose_name='Фамилия', max_length=35, blank=True, null=True)
    NAME = models.CharField(verbose_name='Имя', max_length=35, blank=True, null=True)
    WORK_POSITION = models.CharField(verbose_name='Должность', max_length=100, blank=True, null=True)
    ACTIVE = models.BooleanField(verbose_name='Пользователь активен (не уволен)', default=True, db_index=True)

    def __str__(self):
        return '{} {}'.format(self.LAST_NAME or "-", self.NAME or "")

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


# crm.status.list?filter[ENTITY_ID]=STATUS
class StageLead(models.Model):
    ID = models.PositiveIntegerField(primary_key=True, verbose_name='ID стадии лида в BX24')
    STATUS_ID = models.CharField(verbose_name='Абревиатура стадии лида', max_length=35, db_index=True)
    NAME = models.CharField(verbose_name='Название стадии лида', max_length=100, blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.STATUS_ID or "-", self.NAME or "")

    class Meta:
        verbose_name = 'Стадия лидов'
        verbose_name_plural = 'Стадии лидов'


# crm.status.list?filter[ENTITY_ID]=SOURCE
class Source(models.Model):
    ID = models.PositiveIntegerField(primary_key=True, verbose_name='ID источника в BX24')
    STATUS_ID = models.CharField(verbose_name='Абревиатура источника', max_length=100, db_index=True)
    NAME = models.CharField(verbose_name='Название источника', max_length=200, blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.STATUS_ID or "-", self.NAME or "")

    class Meta:
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'


# STATUS_SEMANTIC_ID
# F (failed) – обработан неуспешно,
# S (success) – обработан успешно,
# P (processing) – лид в обработке.
class StatusSemanticLeads(models.Model):
    STATUS_SEMANTIC_ID = models.CharField(verbose_name='Буквенное обозначение статуса лида', max_length=1, db_index=True)
    STATUS_SEMANTIC_TITLE = models.CharField(verbose_name='Абреаиатура статуса лида', max_length=15, db_index=True)
    TITLE = models.CharField(verbose_name='Описание статуса лида', max_length=50, blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.STATUS_SEMANTIC_ID or "-", self.TITLE or "")

    class Meta:
        verbose_name = 'Семантический статус лида'
        verbose_name_plural = 'Семантические статусы лида'


# crm.lead.list
class Lead(models.Model):
    ID = models.PositiveIntegerField(primary_key=True, verbose_name='ID лида в BX24', unique=True, db_index=True)
    TITLE = models.CharField(verbose_name='Название лида', max_length=35, blank=True, null=True)
    DATE_CREATE = models.DateTimeField(verbose_name='Дата создания лида', blank=True, null=True, db_index=True)
    # DESIGNER = models.CharField(verbose_name='Дизайнер', max_length=100, blank=True, null=True)
    ASSIGNED_BY_ID = models.ForeignKey(User, verbose_name='Ответственный', on_delete=models.CASCADE,
                                       related_name='lead', blank=True, null=True, db_index=True)
    STATUS_ID = models.ForeignKey(StageLead, verbose_name='Стадия лида', on_delete=models.CASCADE,
                                  related_name='lead', blank=True, null=True, db_index=True)
    SOURCE_ID = models.ForeignKey(Source, verbose_name='Источник', on_delete=models.CASCADE,
                                  related_name='lead', blank=True, null=True, db_index=True)
    STATUS_SEMANTIC_ID = models.ForeignKey(StatusSemanticLeads, verbose_name='Источник', on_delete=models.CASCADE,
                                           related_name='lead', blank=True, null=True, db_index=True)

    def __str__(self):
        return '{}. {}'.format(self.ID or "-", self.TITLE or "")

    class Meta:
        verbose_name = 'Лид'
        verbose_name_plural = 'Лиды'


# crm.stagehistory.list?entityTypeId=1&order[CREATED_TIME]=ASC
class LeadStageDuration(models.Model):
    DATE_CREATE = models.DateTimeField(verbose_name='Дата первого перехода на стадию', blank=True, null=True, db_index=True)
    # DURATION = models.PositiveIntegerField(verbose_name='Длительность нахождения на стадии', blank=True, null=True, db_index=True)
    DURATION = models.DurationField(verbose_name='Длительность нахождения на стадии', blank=True, null=True, db_index=True)
    LEAD_ID = models.ForeignKey(Lead, verbose_name='Лид', on_delete=models.CASCADE,
                                related_name='lead_stage_duration', blank=True, null=True, db_index=True)
    STATUS_ID = models.ForeignKey(StageLead, verbose_name='Стадия лида', on_delete=models.CASCADE,
                                  related_name='lead_stage_duration', blank=True, null=True, db_index=True)

    def __str__(self):
        lead_id = self.LEAD_ID.ID if self.LEAD_ID else "-"
        status_id = self.STATUS_ID.STATUS_ID if self.STATUS_ID else "-"
        return '{} - {}'.format(lead_id, status_id)

    class Meta:
        verbose_name = 'Время нахождения лида на стадии'
        verbose_name_plural = 'Время нахождения лидов на стадиях'


