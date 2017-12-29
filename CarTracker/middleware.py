class SetRemoteAddrMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'X_FORWARDED_FOR' in request.META:
            request.META['REMOTE_ADDR'] = request.META['X_FORWARDED_FOR']
        return self.get_response(request)
