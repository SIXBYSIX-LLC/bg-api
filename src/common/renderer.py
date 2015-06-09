"""
Renderer
~~~~~~~~
Change the framework's standard response structure to NewsByMe specific response.

The response design is follow

For single object or data::


    {
        "data": {
        }
    }

For list of object::

    {
        "meta": {
            "count": "TOTAL RECORD COUNT"
            "next": "NEXT PAGE LINK"
            "previous": "PREVIOUS PAGE LINK"
        },
        "data": [
        ]
    }

When error occurs::

    {
        "error": {
            "type": "ERROR TYPE",
            "detail": "HUMAN READABLE MESSAGE",
            "status_code": "APPROPRIATE STATUS CODE"
        }
    }
"""
from rest_framework.renderers import JSONRenderer as RFJSONRenderer


class JSONRenderer(RFJSONRenderer):
    """
    Override the ``render()`` of the rest framework JSONRenderer to produce JSON ouput as per \
    API specification
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_data = {}
        context = 'data'  # Default

        # When exception handler will pass the response, we would expect
        # the context to be `error`
        if data.get('_context') == 'error':
            context = 'error'
            data.pop('_context', None)

            # Normalizing detail field in error, only first element of dict should be visible
            if isinstance(data.get('detail'), dict):
                for k, v in data.get('detail').items():
                    try:
                        detail = '%s: %s' % (k, v[0])
                    except IndexError:
                        detail = '%s: %s' % (k, v)
                    break
                data['detail'] = detail
            elif data.get('non_field_errors'):
                data['detail'] = data.pop('non_field_errors')[0]

        # check if the results have been paginated
        if isinstance(data, dict) and data.has_key('results'):
            # add the resource key and copy the results
            response_data[context] = data.pop('results')
            response_data['meta'] = data
        else:
            response_data[context] = data

        # call super to render the response
        response = super(JSONRenderer, self).render(response_data, accepted_media_type,
                                                    renderer_context)

        return response
