from rest_framework.renderers import JSONRenderer


class StandardJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        status_code = response.status_code if response else 200

        is_success = 200 <= status_code < 400

        standardized_data = {
            "success": is_success,
            "status": status_code,
            "data": data if is_success else None,
            "error": data if not is_success else None,
        }

        return super().render(standardized_data, accepted_media_type, renderer_context)
