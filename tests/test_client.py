import mock
import httplib2
from openstack.compute.client import ComputeClient
from nose.tools import assert_equal
from fakeserver import FakeConfig

fake_response = httplib2.Response({"status": 200})
fake_body = '{"hi": "there"}'
mock_request = mock.Mock(return_value=(fake_response, fake_body))

def client():
    cl = ComputeClient(FakeConfig())
    cl.management_url = "http://example.com"
    cl.auth_token = "token"
    return cl

def test_get():
    cl = client()
    
    @mock.patch.object(httplib2.Http, "request", mock_request)
    @mock.patch('time.time', mock.Mock(return_value=1234))
    def test_get_call():
        resp, body = cl.get("/hi")
        mock_request.assert_called_with("http://example.com/hi?fresh=1234", "GET", 
            headers={"X-Auth-Token": "token", "User-Agent": cl.config.user_agent})
        # Automatic JSON parsing
        assert_equal(body, {"hi":"there"})

    test_get_call()

def test_get_allow_cache():
    cl = client()
    cl.config.allow_cache = True
    
    @mock.patch.object(httplib2.Http, "request", mock_request)
    def test_get_call():
        resp, body = cl.get("/hi")
        # No ?fresh because we're allowing caching.
        mock_request.assert_called_with("http://example.com/hi", "GET", 
            headers={"X-Auth-Token": "token", "User-Agent": cl.config.user_agent})

    test_get_call()
    
def test_post():
    cl = client()
    
    @mock.patch.object(httplib2.Http, "request", mock_request)
    def test_post_call():
        cl.post("/hi", body=[1, 2, 3])
        mock_request.assert_called_with("http://example.com/hi", "POST", 
            headers = {
                "X-Auth-Token": "token",
                "Content-Type": "application/json",
                "User-Agent": cl.config.user_agent},
            body = '[1, 2, 3]'
        )
    
    test_post_call()