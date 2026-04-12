"""
NT Commerce 12.0 - Iteration 78 Code Quality Testing
Tests for code quality improvements:
1. Auth endpoints (unified-login for admin and tenant)
2. /api/auth/me endpoint
3. SaaS endpoints (stats, tenants, plans)
4. Password validation
5. Products and customers (tenant auth)
6. Cache and robots (admin auth)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@ntcommerce.com"
ADMIN_PASSWORD = "Admin@2024"
TENANT_EMAIL = "ncr@ntcommerce.com"
TENANT_PASSWORD = "Test@123"


class TestAuthEndpoints:
    """Test authentication endpoints after code refactoring"""
    
    def test_admin_unified_login(self):
        """Test POST /api/auth/unified-login for super admin"""
        response = requests.post(f"{BASE_URL}/api/auth/unified-login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Missing access_token in response"
        assert "user" in data, "Missing user in response"
        assert data["user"]["email"] == ADMIN_EMAIL
        assert data["user"]["role"] == "super_admin"
        print(f"✅ Admin login successful: {data['user']['email']}")
    
    def test_tenant_unified_login(self):
        """Test POST /api/auth/unified-login for tenant"""
        response = requests.post(f"{BASE_URL}/api/auth/unified-login", json={
            "email": TENANT_EMAIL,
            "password": TENANT_PASSWORD
        })
        assert response.status_code == 200, f"Tenant login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Missing access_token in response"
        assert "user" in data, "Missing user in response"
        assert data["user"]["email"] == TENANT_EMAIL
        print(f"✅ Tenant login successful: {data['user']['email']}")
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/unified-login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code in [401, 404], f"Expected 401/404, got {response.status_code}"
        print("✅ Invalid login correctly rejected")
    
    def test_weak_password_registration(self):
        """Test POST /api/auth/register with weak password returns validation error"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "test_weak@test.com",
            "password": "123",  # Weak password
            "name": "Test User"
        })
        # Should return 400 or 422 for validation error
        assert response.status_code in [400, 422], f"Expected validation error, got {response.status_code}: {response.text}"
        print("✅ Weak password correctly rejected")


class TestAuthMe:
    """Test /api/auth/me endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/unified-login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin login failed")
    
    @pytest.fixture
    def tenant_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/unified-login", json={
            "email": TENANT_EMAIL,
            "password": TENANT_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Tenant login failed")
    
    def test_auth_me_admin(self, admin_token):
        """Test GET /api/auth/me returns admin user info"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        data = response.json()
        assert "email" in data, "Missing email in response"
        assert data["email"] == ADMIN_EMAIL
        print(f"✅ Auth me (admin) returned: {data['email']}")
    
    def test_auth_me_tenant(self, tenant_token):
        """Test GET /api/auth/me returns tenant user info"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {tenant_token}"
        })
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        data = response.json()
        assert "email" in data, "Missing email in response"
        assert data["email"] == TENANT_EMAIL
        print(f"✅ Auth me (tenant) returned: {data['email']}")
    
    def test_auth_me_no_token(self):
        """Test GET /api/auth/me without token returns 401/403"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("✅ Auth me without token correctly rejected")


class TestSaasEndpoints:
    """Test SaaS management endpoints (admin only)"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/unified-login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin login failed")
    
    def test_saas_stats(self, admin_token):
        """Test GET /api/saas/stats returns stats"""
        response = requests.get(f"{BASE_URL}/api/saas/stats", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"SaaS stats failed: {response.text}"
        data = response.json()
        # Should have stats fields
        assert isinstance(data, dict), "Stats should be a dict"
        print(f"✅ SaaS stats returned: {list(data.keys())}")
    
    def test_saas_tenants(self, admin_token):
        """Test GET /api/saas/tenants returns tenant list"""
        response = requests.get(f"{BASE_URL}/api/saas/tenants", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"SaaS tenants failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Tenants should be a list"
        print(f"✅ SaaS tenants returned: {len(data)} tenants")
    
    def test_saas_plans(self, admin_token):
        """Test GET /api/saas/plans returns 3 plans"""
        response = requests.get(f"{BASE_URL}/api/saas/plans", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"SaaS plans failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Plans should be a list"
        assert len(data) >= 3, f"Expected at least 3 plans, got {len(data)}"
        print(f"✅ SaaS plans returned: {len(data)} plans")


class TestTenantEndpoints:
    """Test tenant-specific endpoints (products, customers)"""
    
    @pytest.fixture
    def tenant_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/unified-login", json={
            "email": TENANT_EMAIL,
            "password": TENANT_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Tenant login failed")
    
    def test_products_list(self, tenant_token):
        """Test GET /api/products returns products (tenant auth)"""
        response = requests.get(f"{BASE_URL}/api/products", headers={
            "Authorization": f"Bearer {tenant_token}"
        })
        assert response.status_code == 200, f"Products list failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Products should be a list"
        print(f"✅ Products returned: {len(data)} products")
    
    def test_customers_list(self, tenant_token):
        """Test GET /api/customers returns customers (tenant auth)"""
        response = requests.get(f"{BASE_URL}/api/customers", headers={
            "Authorization": f"Bearer {tenant_token}"
        })
        assert response.status_code == 200, f"Customers list failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Customers should be a list"
        print(f"✅ Customers returned: {len(data)} customers")


class TestAdminOnlyEndpoints:
    """Test admin-only endpoints (cache, robots)"""
    
    @pytest.fixture
    def admin_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/unified-login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin login failed")
    
    @pytest.fixture
    def tenant_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/unified-login", json={
            "email": TENANT_EMAIL,
            "password": TENANT_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Tenant login failed")
    
    def test_cache_stats_admin(self, admin_token):
        """Test GET /api/cache/stats returns cache info (admin auth)"""
        response = requests.get(f"{BASE_URL}/api/cache/stats", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"Cache stats failed: {response.text}"
        data = response.json()
        assert isinstance(data, dict), "Cache stats should be a dict"
        print(f"✅ Cache stats returned: {list(data.keys())}")
    
    def test_robots_status_admin(self, admin_token):
        """Test GET /api/robots/status returns robot status (admin auth)"""
        response = requests.get(f"{BASE_URL}/api/robots/status", headers={
            "Authorization": f"Bearer {admin_token}"
        })
        assert response.status_code == 200, f"Robots status failed: {response.text}"
        data = response.json()
        assert isinstance(data, dict), "Robots status should be a dict"
        # Should have robots field
        if "robots" in data:
            print(f"✅ Robots status returned: {len(data['robots'])} robots")
        else:
            print(f"✅ Robots status returned: {list(data.keys())}")
    
    def test_cache_stats_tenant_forbidden(self, tenant_token):
        """Test GET /api/cache/stats is forbidden for tenant"""
        response = requests.get(f"{BASE_URL}/api/cache/stats", headers={
            "Authorization": f"Bearer {tenant_token}"
        })
        assert response.status_code == 403, f"Expected 403 for tenant, got {response.status_code}"
        print("✅ Cache stats correctly forbidden for tenant")
    
    def test_robots_status_tenant_forbidden(self, tenant_token):
        """Test GET /api/robots/status is forbidden for tenant"""
        response = requests.get(f"{BASE_URL}/api/robots/status", headers={
            "Authorization": f"Bearer {tenant_token}"
        })
        assert response.status_code == 403, f"Expected 403 for tenant, got {response.status_code}"
        print("✅ Robots status correctly forbidden for tenant")


class TestNoIdLeaks:
    """Test that MongoDB _id is not leaked in responses"""
    
    @pytest.fixture
    def tenant_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/unified-login", json={
            "email": TENANT_EMAIL,
            "password": TENANT_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Tenant login failed")
    
    def test_products_no_id_leak(self, tenant_token):
        """Test products response doesn't contain _id"""
        response = requests.get(f"{BASE_URL}/api/products", headers={
            "Authorization": f"Bearer {tenant_token}"
        })
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                assert "_id" not in first_item, f"_id leaked in products: {first_item.keys()}"
                print("✅ Products response has no _id leak")
            else:
                print("⚠️ No products to check for _id leak")
        else:
            pytest.skip("Products endpoint failed")
    
    def test_customers_no_id_leak(self, tenant_token):
        """Test customers response doesn't contain _id"""
        response = requests.get(f"{BASE_URL}/api/customers", headers={
            "Authorization": f"Bearer {tenant_token}"
        })
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                assert "_id" not in first_item, f"_id leaked in customers: {first_item.keys()}"
                print("✅ Customers response has no _id leak")
            else:
                print("⚠️ No customers to check for _id leak")
        else:
            pytest.skip("Customers endpoint failed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
