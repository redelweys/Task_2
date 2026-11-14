import random

import pytest
import requests

from urls import INGREDIENTS_URL, ORDERS_URL, REGISTER_URL, USER_URL


@pytest.fixture
def user_data():
    suffix = random.randint(100000000000, 999999999999)

    return {
        'email': f'qa_student_{suffix}@example.com',
        'password': 'TestPassword123!',
        'name': 'Test User',
    }


@pytest.fixture
def user_cleanup():
    tokens = []

    yield tokens

    for token in tokens:
        response = requests.delete(
            USER_URL,
            headers={'Authorization': token},
            timeout=30,
        )
        response.raise_for_status()
        assert response.json()['success'] is True

@pytest.fixture
def registered_user(user_data, user_cleanup):
    response = requests.post(
        REGISTER_URL,
        json=user_data,
        timeout=30,
    )
    body = response.json()

    token = body.get('accessToken')
    if token:
        user_cleanup.append(token)

    assert response.status_code == 200
    assert body['success'] is True
    assert token

    return {
        'data': user_data.copy(),
        'token': token,
    }

@pytest.fixture
def ingredient_ids():
    response = requests.get(INGREDIENTS_URL, timeout=30)

    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True

    ingredients = body['data']
    bun = next(item for item in ingredients if item['type'] == 'bun')
    filling = next(item for item in ingredients if item['type'] == 'main')

    return [bun['_id'], filling['_id']]

@pytest.fixture
def user_with_order(registered_user, ingredient_ids):
    response = requests.post(
        ORDERS_URL,
        headers={'Authorization': registered_user['token']},
        json={'ingredients': ingredient_ids},
        timeout=30,
    )

    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True

    return {
        'token': registered_user['token'],
        'order_number': body['order']['number'],
    }