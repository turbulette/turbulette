import pytest
from async_asgi_testclient import TestClient

from turbulette import turbulette
from turbulette.conf.exceptions import ImproperlyConfigured


@pytest.mark.asyncio
async def test_csrf(blank_conf):
    app = turbulette("tests.settings_csrf")
    from turbulette.cache import cache
    from turbulette.conf import settings
    from turbulette.conf.utils import settings_stub

    async with TestClient(app) as client:

        resp = await client.get("/csrf")
        assert resp.status_code == 200
        assert "csrftoken" in resp.json()

        csrf_token = resp.json()["csrftoken"]

        # Safe method
        resp = await client.get("/welcome")
        assert resp.status_code == 200

        # No cookie, no header
        resp = await client.post("/welcome")
        assert resp.status_code == 403

        # No cookie
        resp = await client.post(
            "/welcome", headers={settings.CSRF_HEADER_NAME: csrf_token}
        )
        assert resp.status_code == 403

        # No header
        resp = await client.post(
            "/welcome", cookies={settings.CSRF_HEADER_NAME: csrf_token}
        )
        assert resp.status_code == 403

        # Cookie + header : everything is good
        resp = await client.post(
            "/welcome",
            cookies={settings.CSRF_COOKIE_NAME: csrf_token},
            headers={settings.CSRF_HEADER_NAME: csrf_token},
        )
        assert resp.status_code == 200

        with settings_stub(CSRF_FORM_PARAM=True, CSRF_HEADER_PARAM=False):
            # Cookie + form : everything is good
            resp = await client.post(
                "/welcome",
                cookies={settings.CSRF_COOKIE_NAME: csrf_token},
                form={settings.CSRF_COOKIE_NAME: csrf_token},
            )
            assert resp.status_code == 200

            # No form
            resp = await client.post(
                "/welcome", form={settings.CSRF_COOKIE_NAME: csrf_token}
            )
            assert resp.status_code == 403

        # No referrer
        resp = await client.post(
            "/welcome",
            cookies={settings.CSRF_COOKIE_NAME: csrf_token},
            headers={settings.CSRF_HEADER_NAME: csrf_token},
            scheme="https",
        )
        assert resp.status_code == 403

        with settings_stub(ALLOWED_HOSTS=["api.io"]):
            # Valid referer
            resp = await client.post(
                "/welcome",
                cookies={settings.CSRF_COOKIE_NAME: csrf_token},
                headers={
                    settings.CSRF_HEADER_NAME: csrf_token,
                    "referer": "https://api.io",
                },
                scheme="https",
            )
            assert resp.status_code == 200

        with settings_stub(CSRF_FORM_PARAM=False, CSRF_HEADER_PARAM=False):
            with pytest.raises(ImproperlyConfigured):
                # No submit method set
                resp = await client.post(
                    "/welcome",
                    cookies={settings.CSRF_COOKIE_NAME: csrf_token},
                    headers={
                        settings.CSRF_HEADER_NAME: csrf_token,
                    },
                    scheme="http",
                )
                assert resp.status_code == 403

    # Reconnect to cache to not perturb other tests
    await cache.connect()
