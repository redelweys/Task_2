import allure
import pytest
import requests

from urls import ORDERS_URL


class TestCreateOrder:

    @allure.title('Создание заказа с авторизацией и ингредиентами')
    def test_create_order_with_authorization_returns_order(
        self, registered_user, ingredient_ids
    ):
        response = requests.post(
            ORDERS_URL,
            headers={'Authorization': registered_user['token']},
            json={'ingredients': ingredient_ids},
            timeout=30,
        )

        assert response.status_code == 200
        body = response.json()
        assert body['success'] is True
        assert isinstance(body['name'], str) and body['name']
        assert type(body['order']['number']) is int
        assert body['order']['number'] > 0

    @allure.title('Создание заказа без ингредиентов')
    @pytest.mark.parametrize('authorized', [True, False])
    def test_create_order_without_ingredients_returns_error(
        self, registered_user, authorized
    ):
        headers = {}
        if authorized:
            headers['Authorization'] = registered_user['token']

        response = requests.post(
            ORDERS_URL,
            headers=headers,
            json={'ingredients': []},
            timeout=30,
        )

        assert response.status_code == 400
        assert response.json() == {
            'success': False,
            'message': 'Ingredient ids must be provided',
        }

    @allure.title('Создание заказа с неверным хешем ингредиента')
    def test_create_order_with_invalid_ingredient_hash_returns_error(
        self, registered_user
    ):
        response = requests.post(
            ORDERS_URL,
            headers={'Authorization': registered_user['token']},
            json={'ingredients': ['invalid_hash']},
            timeout=30,
        )

        allure.attach(
            response.text,
            name=f'Ответ сервера, HTTP {response.status_code}',
            attachment_type=allure.attachment_type.TEXT,
        )

        assert response.status_code == 500, (
            f'Ожидали HTTP 500, получили {response.status_code}. '
            f'Тело ответа: {response.text}'
        )

    @allure.title('Создание заказа с ингредиентами без авторизации')
    def test_create_order_without_authorization_returns_error(
        self, ingredient_ids
    ):
        response = requests.post(
            ORDERS_URL,
            json={'ingredients': ingredient_ids},
            timeout=30,
        )

        allure.attach(
            response.text,
            name=f'Ответ сервера, HTTP {response.status_code}',
            attachment_type=allure.attachment_type.TEXT,
        )

        assert response.status_code == 401, (
            f'Ожидали HTTP 401, получили {response.status_code}. '
            f'Тело ответа: {response.text}'
        )
        assert response.json()['success'] is False