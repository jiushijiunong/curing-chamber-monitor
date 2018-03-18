class SoapRequest(object):
    def __init__(self, location=None, action=None, method=None, namespace="http://tempuri.org/", soap_ns="s",
                 soap_namespace="http://schemas.xmlsoap.org/soap/envelope/"):

        self.location = location  # server location (url)
        self.action = action  # SOAP base action
        self.method = method
        self.__xml = "".join(["""<%(soap_ns)s:Envelope xmlns:%(soap_ns)s="%(soap_namespace)s" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        <%(soap_ns)s:Body><%(method)s xmlns="%(namespace)s">""" %
                              dict(method=self.method, soap_namespace=soap_namespace, namespace=namespace,
                                   soap_ns=soap_ns),
                              "%(method_args)s",
                              """</%(method)s></%(soap_ns)s:Body></%(soap_ns)s:Envelope>""" %
                              dict(method=self.method, soap_ns=soap_ns)])

    def parse(self, **kwargs):
        order_arg_name = "__order_list"
        if kwargs:
            order = kwargs.get(order_arg_name, "")
            if order:
                sorted_keys = sorted([k for k in kwargs if k != order_arg_name], key=order.index)
                parameters = [(k, kwargs.get(k)) for k in sorted_keys]
            else:
                parameters = list(kwargs.items())

        else:
            parameters = []

        method_args = []
        method_arg_pattern = "<%(method_arg)s>%(method_arg_value)s</%(method_arg)s>"
        for k, v in parameters:
            if v is not None:
                value = v
                if isinstance(v, bool):
                    value = str(v).lower()
                method_args.append(method_arg_pattern % dict(method_arg=k, method_arg_value=value))
        return self.__xml % dict(method_args="".join(method_args))


