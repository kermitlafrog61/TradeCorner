import logging

logger = logging.getLogger('user_logger')

class LogUserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            logger.info(f"{request.user.username} accessed {request.method} {request.path}")
        return response
