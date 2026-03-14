"""
실습 2 정답 모음
"""

# parse_request:
#   parts = raw_request.split("\r\n\r\n")
#   result["method"] = request_line[0]
#   result["path"] = request_line[1]
#   result["version"] = request_line[2]
#   key, value = line.split(": ", 1)

# build_response:
#   status_line = f"HTTP/1.1 {status_code} {status_text}\r\n"
#   headers += f"Content-Type: {content_type}\r\n"
#   headers += f"Content-Length: {len(body)}\r\n"
#   response = (status_line + headers + "\r\n").encode("utf-8") + body

# handle_get:
#   return build_response(200, "OK", body, content_type)
#   return build_response(404, "Not Found", body)

# run_server:
#   response = handle_get(request["path"])
#   response = handle_post(request["path"], request["body"])
