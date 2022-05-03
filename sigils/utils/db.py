from tortoise import fields
from tortoise.models import Model


class Quote(Model):
    id = fields.BigIntField(pk=True)

    message_id = fields.CharField(max_length=20, unique=True)
    guild_id = fields.TextField()
    channel_id = fields.TextField()
    author_id = fields.TextField()

    num = fields.IntField()

    content = fields.TextField()

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_add=True)

    class Meta:
        table = "quotes"
        unique_together = ("guild_id", "num")

    def __str__(self):
        return self.id
