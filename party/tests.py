import json
from io import BytesIO
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from party.models.locations import County, Constituency, Ward
from party.models.membership import Membership


class MembershipPaystackTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.county = County.objects.create(name='Test County')
        self.constituency = Constituency.objects.create(name='Test Constituency', county=self.county)
        self.ward = Ward.objects.create(name='Test Ward', constituency=self.constituency)
        self.payload = {
            'reference': 'paystack-test-reference',
            'membership': {
                'membership_type': 'bronze',
                'first_name': 'Test',
                'last_name': 'Member',
                'email': 'member@example.com',
                'phone': '+254700000000',
                'age': 30,
                'gender': 'other',
                'occupation': 'Tester',
                'county': self.county.id,
                'constituency': self.constituency.id,
                'ward': self.ward.id,
            },
        }

    @override_settings(PAYSTACK_SECRET_KEY='test-secret')
    @patch('party.views.views.urlopen')
    @patch.object(Membership, 'is_free_registration_period', return_value=False)
    def test_verified_paystack_payment_creates_completed_guest_membership(self, mock_free_period, mock_urlopen):
        mock_urlopen.return_value = BytesIO(json.dumps({
            'status': True,
            'data': {
                'status': 'success',
                'reference': 'paystack-test-reference',
                'currency': 'KES',
                'amount': 500000,
                'customer': {'email': 'member@example.com'},
            },
        }).encode())

        response = self.client.post(
            '/api/memberships/verify-payment/',
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['payment_status'], 'completed')
        self.assertEqual(response.data['payment_method'], 'paystack')
        self.assertEqual(response.data['transaction_id'], self.payload['reference'])
        self.assertEqual(Membership.objects.count(), 1)
        mock_urlopen.assert_called_once()

    @override_settings(PAYSTACK_SECRET_KEY='test-secret')
    @patch('party.views.views.urlopen')
    @patch.object(Membership, 'is_free_registration_period', return_value=False)
    def test_repeating_verified_reference_does_not_create_duplicate_membership(self, mock_free_period, mock_urlopen):
        mock_urlopen.return_value = BytesIO(json.dumps({
            'status': True,
            'data': {
                'status': 'success',
                'reference': 'paystack-test-reference',
                'currency': 'KES',
                'amount': 500000,
                'customer': {'email': 'member@example.com'},
            },
        }).encode())
        first_response = self.client.post(
            '/api/memberships/verify-payment/',
            self.payload,
            format='json',
        )
        second_response = self.client.post(
            '/api/memberships/verify-payment/',
            self.payload,
            format='json',
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(Membership.objects.count(), 1)
        mock_urlopen.assert_called_once()

    @override_settings(PAYSTACK_SECRET_KEY='test-secret')
    @patch('party.views.views.urlopen')
    @patch.object(Membership, 'is_free_registration_period', return_value=False)
    def test_payment_with_wrong_amount_does_not_create_membership(self, mock_free_period, mock_urlopen):
        mock_urlopen.return_value = BytesIO(json.dumps({
            'status': True,
            'data': {
                'status': 'success',
                'reference': 'paystack-test-reference',
                'currency': 'KES',
                'amount': 1,
                'customer': {'email': 'member@example.com'},
            },
        }).encode())

        response = self.client.post(
            '/api/memberships/verify-payment/',
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Membership.objects.count(), 0)

    @override_settings(PAYSTACK_SECRET_KEY=None)
    def test_payment_verification_requires_backend_secret_key(self):
        response = self.client.post(
            '/api/memberships/verify-payment/',
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(Membership.objects.count(), 0)

    @patch.object(Membership, 'is_free_registration_period', return_value=True)
    def test_paid_plan_registration_is_free_before_deadline(self, mock_free_period):
        payload = {
            **self.payload['membership'],
            'membership_type': 'mca',
        }
        response = self.client.post('/api/memberships/public/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['payment_status'], 'completed')
        self.assertEqual(response.data['amount'], '0.00')
        self.assertEqual(Membership.objects.count(), 1)

    @patch.object(Membership, 'is_free_registration_period', return_value=False)
    def test_public_endpoint_rejects_paid_plan_after_deadline_but_keeps_mwananchi_free(self, mock_free_period):
        payload = {
            **self.payload['membership'],
            'membership_type': 'mca',
        }
        response = self.client.post('/api/memberships/public/', payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Membership.objects.count(), 0)

        payload = {
            **self.payload['membership'],
            'membership_type': 'mwananchi',
        }
        response = self.client.post('/api/memberships/public/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['payment_status'], 'completed')
        self.assertEqual(Membership.objects.count(), 1)

    @override_settings(PAYSTACK_SECRET_KEY='test-secret')
    @patch('party.views.views.urlopen')
    @patch.object(Membership, 'is_free_registration_period', return_value=False)
    def test_youth_pwd_rate_is_verified_and_saved(self, mock_free_period, mock_urlopen):
        self.payload['membership'].update({
            'membership_type': 'mca',
            'membership_category': 'youth_pwd',
        })
        mock_urlopen.return_value = BytesIO(json.dumps({
            'status': True,
            'data': {
                'status': 'success',
                'reference': 'paystack-test-reference',
                'currency': 'KES',
                'amount': 250000,
                'customer': {'email': 'member@example.com'},
            },
        }).encode())

        response = self.client.post(
            '/api/memberships/verify-payment/',
            self.payload,
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['membership_category'], 'youth_pwd')
        self.assertEqual(response.data['amount'], '2500.00')
