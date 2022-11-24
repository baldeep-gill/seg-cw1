from lessons.models import LessonRequest

# for future use
class LogInTester:
    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()

def create_requests(author, from_count, to_count):
    """Create unique numbered requests for testing purposes."""
    for count in range(from_count, to_count):
        text = f'Request__{count}'
        request = LessonRequest(
            author=author, 
            availability = text,
            lessonNum = 1,
            interval = 1,
            duration = 60,
            topic = "temp",
            teacher = "temp"
        )
        request.save()