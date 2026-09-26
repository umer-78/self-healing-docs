## httpx, whole history

- Breaking API changes the docs were using: 38
- Docs updated in the same commit: 13
- Left doc sections stale: 25 changes, 33 sections
- Of those sections, fixed later: 15, after a median of 1 commits to the file and 52 days
- Made right again by the code (the removed name came back): 13
- Still stale at the pinned commit: 5
- Argument renames the docs used: 11 sections; the mechanical fix was suggested for 11 and matches the maintainers' own edit in 8

| Commit | Change | Doc section | Why | Fixed |
|---|---|---|---|---|
| 92fbe5fd87 | httpx.exceptions:HttpError removed | docs/quickstart.md > QuickStart > Response Status Codes | uses HttpError, which was removed | 17 commits, 301 days later |
| 206c5372a6 | httpx.client:AsyncClient removed | docs/advanced.md > Advanced Usage > Support async environments > [asyncio](https://docs.python.org/3/library/asyncio.html) (Default) | uses AsyncClient, which was removed | 1 commits, 1 days later |
| 206c5372a6 | httpx.client:AsyncClient removed | docs/advanced.md > Advanced Usage > Support async environments > [trio](https://github.com/python-trio/trio) | uses AsyncClient, which was removed | 1 commits, 1 days later |
| 30229f1652 | httpx.config:HTTPVersionConfig removed | docs/environment_variables.md > docs/environment_variables.md | uses HTTPVersionConfig, which was removed | 14 commits, 1204 days later |
| ec40d04382 | httpx.models:Response.stream_bytes removed | docs/api.md > Developer Interface > `Response` | uses Response.stream_bytes, which was removed | 1 commits, 15 days later |
| ec40d04382 | httpx.models:Response.stream_text removed | docs/api.md > Developer Interface > `Response` | uses Response.stream_text, which was removed | 1 commits, 15 days later |
| ec40d04382 | httpx.models:Response.stream_lines removed | docs/api.md > Developer Interface > `Response` | uses Response.stream_lines, which was removed | 1 commits, 15 days later |
| ec40d04382 | httpx.models:Response.stream_raw removed | docs/api.md > Developer Interface > `Response` | uses Response.stream_raw, which was removed | 1 commits, 15 days later |
| e284b84bf9 | httpx.client:Client removed | docs/advanced.md > Advanced Usage > Client Instances | uses Client, which was removed | the name came back 10 days later |
| e284b84bf9 | httpx.client:Client removed | docs/advanced.md > Advanced Usage > Client Instances > Usage | uses Client, which was removed | the name came back 10 days later |
| e284b84bf9 | httpx.client:Client removed | docs/advanced.md > Advanced Usage > Client Instances > Configuration | uses Client, which was removed | the name came back 10 days later |
| e284b84bf9 | httpx.client:Client removed | docs/advanced.md > Advanced Usage > .netrc Support | uses Client, which was removed | the name came back 10 days later |
| e284b84bf9 | httpx.client:Client removed | docs/advanced.md > Advanced Usage > HTTP Proxying | uses Client, which was removed | the name came back 10 days later |
| e284b84bf9 | httpx.client:Client removed | docs/advanced.md > Advanced Usage > SSL certificates > SSL configuration on client instances | uses Client, which was removed | the name came back 10 days later |
| e284b84bf9 | httpx.client:Client removed | docs/api.md > Developer Interface > Helper Functions | uses Client, which was removed | the name came back 10 days later |
| e284b84bf9 | httpx.client:Client removed | docs/compatibility.md > Requests Compatibility Guide > SSL configuration | uses Client, which was removed | the name came back 10 days later |
| 3046e920ea | httpx._client:AsyncClient parameter removed `uds` | docs/async.md > Async Support > Unix Domain Sockets | passes uds= to AsyncClient(), which no longer takes it | 2 commits, 52 days later |
| 3046e920ea | httpx._dispatch.connection:HTTPConnection removed | docs/environment_variables.md > docs/environment_variables.md | uses HTTPConnection, which was removed | 9 commits, 1076 days later |
| 3046e920ea | httpx._exceptions:TimeoutException removed | docs/advanced.md > Advanced Usage > Timeout Configuration | uses TimeoutException, which was removed | the name came back 86 days later |
| 3046e920ea | httpx._exceptions:ConnectTimeout removed | docs/advanced.md > Advanced Usage > Timeout Configuration > Fine tuning the configuration | uses ConnectTimeout, which was removed | the name came back 86 days later |
| 3046e920ea | httpx._exceptions:ReadTimeout removed | docs/advanced.md > Advanced Usage > Timeout Configuration > Fine tuning the configuration | uses ReadTimeout, which was removed | the name came back 86 days later |
| 3046e920ea | httpx._exceptions:WriteTimeout removed | docs/advanced.md > Advanced Usage > Timeout Configuration > Fine tuning the configuration | uses WriteTimeout, which was removed | the name came back 86 days later |
| 3046e920ea | httpx._exceptions:PoolTimeout removed | docs/advanced.md > Advanced Usage > Timeout Configuration > Fine tuning the configuration | uses PoolTimeout, which was removed | the name came back 86 days later |
| 247ee0dc49 | httpx._models:Origin removed | docs/environment_variables.md > docs/environment_variables.md | uses Origin, which was removed | 9 commits, 970 days later |
| 8fa87650b2 | httpx._transports.urllib3:URLLib3Transport removed | docs/advanced.md > Advanced Usage > Custom Transports > urllib3 transport | uses URLLib3Transport, which was removed | 35 commits, 1228 days later |
| f932af9172 | httpx._config:Limits parameter removed `max_keepalive` | docs/advanced.md > Advanced Usage > Pool limit configuration | passes max_keepalive= to Limits(), which no longer takes it | 1 commits, 1 days later |
| 0eed6a3734 | httpx._models:Response.next removed | docs/api.md > Developer Interface > `Response` | uses Response.next, which was removed | not yet |
| 0eed6a3734 | httpx._models:Response.anext removed | docs/api.md > Developer Interface > `Response` | uses Response.anext, which was removed | not yet |
| 77246617ca | httpx._config:Proxy parameter removed `mode` | docs/advanced.md > Advanced Usage > HTTP Proxying > Proxy mechanisms > Forcing the proxy mechanism | passes mode= to Proxy(), which no longer takes it | 4 commits, 159 days later |
| 47266d763b | httpx._client:Client.send parameter removed `allow_redirects` | docs/compatibility.md > Requests Compatibility Guide > Determining the next redirect request | passes allow_redirects= to send(), which no longer takes it | not yet |
| 47266d763b | httpx._client:AsyncClient.send parameter removed `allow_redirects` | docs/compatibility.md > Requests Compatibility Guide > Determining the next redirect request | passes allow_redirects= to send(), which no longer takes it | not yet |
| 61188feeae | httpx._transports.default:AsyncHTTPTransport parameter removed `backend` | docs/async.md > Async Support > Supported async environments > [AnyIO](https://github.com/agronholm/anyio) | passes backend= to AsyncHTTPTransport(), which no longer takes it | 1 commits, 56 days later |
| 1805ee0d22 | httpx._config:SSLContext removed | docs/logging.md > Logging | uses SSLContext, which was removed | not yet |
