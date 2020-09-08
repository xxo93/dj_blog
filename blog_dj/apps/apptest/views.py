from rest_framework.decorators import api_view, action
from rest_framework.response import Response


@api_view(["GET"])
def test(request):
    """ 测试
    :param request:
    :return:
    """
    print('...........test api')
    return Response({
        'code': '200',
        'msg': 'ok',
    })