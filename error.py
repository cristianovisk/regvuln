import coloredlogs, logging

errors = {"100":"Continue","101":"Switching Protocols","102":"Processing","200":"OK","201":"Created","202":"Accepted","203":"Non-authoritative Information","204":"No Content","205":"Reset Content","206":"Partial Content","207":"Multi-Status","208":"Already Reported","226":"IM Used","300":"Multiple Choices","301":"Moved Permanently","302":"Found","303":"See Other","304":"Not Modified","305":"Use Proxy","307":"Temporary Redirect","308":"Permanent Redirect","400":"Bad Request","401":"Unauthorized","402":"Payment Required","403":"Forbidden","404":"Not Found","405":"Method Not","406":"Not Acceptable","407":"Proxy Authentication","408":"Request Timeout","409":"Conflict","410":"Gone","411":"Length Required","412":"Precondition Failed","413":"Payload Too","414":"Request-URI Too","415":"Unsupported Media","416":"Requested Range","417":"Expectation Failed","418":"I m a","421":"Misdirected Request","422":"Unprocessable Entity","423":"Locked","424":"Failed Dependency","426":"Upgrade Required","428":"Precondition Required","429":"Too Many","431":"Request Header","444":"Connection Closed","451":"Unavailable For","499":"Client Closed","500":"Internal Server","501":"Not Implemented","502":"Bad Gateway","503":"Service Unavailable","504":"Gateway Timeout","505":"HTTP Version","506":"Variant Also","507":"Insufficient Storage","508":"Loop Detected","510":"Not Extended","511":"Network Authentication","599":"Network Connect"}

# coloredlogs.install()

def handlingError(content, status_code):
    # content = content.decode('utf-8')
    if status_code >= 100 and status_code < 200:
        try:
            logging.debug("HTTP %i - %s"%(int(status_code),errors["%s" %status_code]))
            logging.debug("Content: %s" %content)
        except:
            logging.debug("HTTP Error Not Correct to Interpreter")
    elif status_code >= 200 and status_code < 300:
        try:
            logging.debug("HTTP %i - %s"%(int(status_code),errors["%s" %status_code]))
            logging.debug("Content: %s" %content)
        except:
            logging.debug("HTTP Error Not Correct to Interpreter")
    elif status_code >= 300 and status_code < 400:
        try:
            logging.debug("HTTP %i - Description: %s"%(int(status_code),errors["%s" %status_code]))
            logging.debug("Content: %s" %content)
        except:
            logging.debug("HTTP Error Not Correct to Interpreter")
    elif status_code >= 400 and status_code < 500:
        try:
            logging.debug("HTTP %i - Description: %s"%(int(status_code),errors["%s" %status_code]))
            logging.debug("Content: %s" %content)
        except:
            logging.debug("HTTP Error Not Correct to Interpreter")
    elif status_code >= 500 and status_code < 600:
        try:
            logging.debug("HTTP %i - Description: %s"%(int(status_code),errors["%s" %status_code]))
            logging.debug("Content: %s" %content)
        except:
            logging.debug("HTTP Error Not Correct to Interpreter")

# handlingError("Teste Error", 200)