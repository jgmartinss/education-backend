import pytest
from decimal import Decimal

from orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('bundle'),
]


def get_order():
    return Order.objects.last()


def test_order(api, bundle):
    api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.item == bundle
    assert placed.price == Decimal('1900.00')


def test_user(api, bundle):
    api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.user.first_name == 'Забой'
    assert placed.user.last_name == 'Шахтёров'
    assert placed.user.email == 'zaboy@gmail.com'


@pytest.mark.parametrize('wants_to_subscribe', [True, False])
def test_user_auto_subscription(api, wants_to_subscribe):
    api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
        'subscribe': wants_to_subscribe,
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.user.subscribed is wants_to_subscribe


def test_by_default_user_is_not_subscribed(api):
    api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.user.subscribed is False


def test_redirect(api, bundle):
    response = api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
    }, format='multipart', expected_status_code=302, as_response=True)

    assert response.status_code == 302
    assert response['Location'] == 'https://bank.test/pay/'


def test_custom_success_url(api, bundle, bank):
    api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
        'success_url': 'https://ok.true/yes',
    }, format='multipart', expected_status_code=302)

    assert bank.call_args[1]['success_url'] == 'https://ok.true/yes'


def test_invalid(client):
    response = client.post('/api/v2/bundles/pinetree-tickets/purchase/', {})

    assert response.status_code == 400
