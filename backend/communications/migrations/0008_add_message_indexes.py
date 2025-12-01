from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("communications", "0007_add_message_reactions"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="communicationmessage",
            index=models.Index(
                fields=["thread", "-sent_at"],
                name="comm_msg_thread_sent_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="communicationmessage",
            index=models.Index(
                fields=["thread", "is_read"],
                name="comm_msg_thread_read_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="communicationmessage",
            index=models.Index(
                fields=["sender", "-sent_at"],
                name="comm_msg_sender_sent_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="communicationmessage",
            index=models.Index(
                fields=["recipient", "-sent_at"],
                name="comm_msg_recipient_sent_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="communicationmessage",
            index=models.Index(
                fields=["thread", "is_deleted"],
                name="comm_msg_thread_deleted_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="communicationmessage",
            index=models.Index(
                fields=["thread", "is_archived"],
                name="comm_msg_thread_archived_idx",
            ),
        ),
    ]


