import random
import string
from datetime import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from apps.submissions.models import Submission


WORDS = (
    "alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima ".split()
    + "miserable project retro crt terminal pixel vintage keyboard click ".split()
    + "backend api cache queue worker deploy failure lesson idea tech stack".split()
)


def rand_words(n: int) -> str:
    return " ".join(random.choice(WORDS) for _ in range(n))


def sentence(n: int = 8) -> str:
    s = rand_words(n).capitalize()
    return s + "."


def paragraph(sentences: int = 4) -> str:
    return "\n\n".join(sentence(random.randint(6, 12)) for _ in range(sentences))


def markdown_block() -> str:
    # Simple markdown-ish content without H1/H2 (stripper removes them anyway)
    blocks = [
        paragraph(random.randint(2, 4)),
        "- " + "\n- ".join(rand_words(random.randint(3, 7)) for _ in range(random.randint(2, 4))),
        paragraph(random.randint(2, 3)),
    ]
    return "\n\n".join(blocks)


class Command(BaseCommand):
    help = "Create random submissions for local testing."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10, help="How many submissions to create")
        parser.add_argument(
            "--user",
            type=str,
            default="seed",
            help="Username to assign as author (created if missing)",
        )

    def handle(self, *args, **opts):
        count = max(1, int(opts["count"]))
        username = opts["user"]
        User = get_user_model()
        user, _ = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})
        created = 0
        for i in range(count):
            name = (rand_words(random.randint(2, 4)) + " " + rand_words(1)).title()
            tagline = sentence(random.randint(6, 10))
            is_anon = random.random() < 0.3
            birth_year = random.randint(2000, datetime.utcnow().year)
            lifespan = random.choice([None, random.randint(1, 48)])
            links = []
            if random.random() < 0.4:
                links.append("https://example.com/" + slugify(rand_words(2)))
            if random.random() < 0.3:
                links.append("https://github.com/" + slugify(rand_words(2)))

            s = Submission(
                user=user,
                project_name=name,
                tagline=tagline,
                description=markdown_block(),
                idea=markdown_block(),
                tech=markdown_block(),
                failure=markdown_block(),
                lessons=markdown_block(),
                wins=paragraph(random.randint(1, 2)),
                is_anonymous=is_anon,
                birth_year=birth_year,
                lifespan=lifespan,
                links_json=links,
                status="published",
            )
            s.save()
            # tags
            tags = list({random.choice(["python", "django", "react", "redis", "celery", "postgres", "docker", "aws"]) for _ in range(random.randint(1, 4))})
            if tags:
                s.stack_tags.add(*tags)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} submissions (user @{user.username})."))

