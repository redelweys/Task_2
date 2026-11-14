import allure
import requests

from urls import ORDERS_URL


class TestGetUserOrders:

    @allure.title('Получение заказов авторизованного пользователя')
    def test_get_user_orders_with_authorization_returns_created_order(
        self, user_with_order
    ):
        response = requests.get(
            ORDERS_URL,
            headers={'Authorization': user_with_order['token']},
            timeout=30,
        )

        assert response.status_code == 200
        body = response.json()
        assert body['success'] is True
        assert isinstance(body['orders'], list)
        assert user_with_order['order_number'] in [
            order['number'] for order in body['orders']
        ]

    @allure.title('Получение заказов без авторизации')
    def test_get_user_orders_without_authorization_returns_error(self):
        response = requests.get(
            ORDERS_URL,
            timeout=30,
        )

        assert response.status_code == 401
        assert response.json() == {
            'success': False,
            'message': 'You should be authorised',
        }