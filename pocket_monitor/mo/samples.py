# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from soap_request import SoapRequest
from soap_response import SoapResponse
import pocket_monitor.http as http


class BaseRetriever(object):
    def __init__(self, location=None, action=None, method=None):
        self.req = SoapRequest(location=location, action=action,  method=method)
        self.headers = {
            'Content-type': 'text/xml; charset="UTF-8"',
            'Accept-Language': 'zh-CN',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'Keep-Alive',
            'Host': 'www.scetia.com',
            'DNT': 1,
            'Cache-Control': 'no-cache',
            'SOAPAction': self.req.action + self.req.method
        }

    def retrieve(self, **kwargs):
        soap_xml = self.req.parse(**kwargs)
        headers = self.headers.copy()
        headers['Content-length'] = str(len(soap_xml))
        rep_code, rep_content = http.post(url=self.req.location, body=soap_xml, headers=headers)

        return SoapResponse(rep_code=rep_code, rep_content=rep_content)


# http://www.scetia.com/Scetia.SampleManage.WCF/Item.svc
# SOAPAction: http://tempuri.org/IItem/GetItemSeries
# Request: <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><GetItemSeries xmlns="http://tempuri.org/" /></s:Body></s:Envelope>
class ItemRetriever(BaseRetriever):
    def __init__(self):
        super(ItemRetriever, self).__init__("http://www.scetia.com/Scetia.SampleManage.WCF/Item.svc",
                                            "http://tempuri.org/IItem/",
                                            "GetItemSeries")

    def retrieve(self):
        rep = super(ItemRetriever, self).retrieve()
        return rep.rep_code, rep.get_response_entities("GetItemSeriesResult")


# http://www.scetia.com/Scetia.SampleManage.WCF/Project.svc
#﻿SOAPAction: http://tempuri.org/IProject/GetProjectsForBuildUnit
# Request: <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><GetProjectsForBuildUnit xmlns="http://tempuri.org/"><buildUnitId>394eb96f-e57b-4b0a-bb29-0f1fbddfaeb6</buildUnitId><pageSize>20</pageSize><pageNum>1</pageNum><buildUnitUserId>0752221a-fa3e-4211-a3b9-e1c8886edd76</buildUnitUserId><queryStr xsi:nil="true" /><notFinishedOnly>true</notFinishedOnly></GetProjectsForBuildUnit></s:Body></s:Envelope>
class ProjectRetriever(BaseRetriever):
    def __init__(self):
        super(ProjectRetriever, self).__init__("http://www.scetia.com/Scetia.SampleManage.WCF/Project.svc",
                                               "http://tempuri.org/IProject/",
                                               "GetProjectsForBuildUnit")

    def retrieve(self, build_unit_id=None, build_unit_user_id=None,
                 not_finished_only=True, query_str='', page_num=1, page_size=20):
        rep = super(ProjectRetriever, self).retrieve(buildUnitId=build_unit_id,
                                                      queryStr=query_str,
                                                      buildUnitUserId=build_unit_user_id,
                                                      notFinishedOnly=not_finished_only,
                                                      pageNum=page_num,
                                                      pageSize=page_size,
                                                      __order_list=["buildUnitId", "pageSize", "pageNum",
                                                                   "buildUnitUserId", "queryStr", "notFinishedOnly"])
        return rep.rep_code, rep.get_response_entities("GetProjectsForBuildUnitResult")

# http://www.scetia.com/Scetia.SampleManage.WCF/Contract.svc
# SOAPAction: http://tempuri.org/IContract/GetContract
# Request: <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><GetContract xmlns="http://tempuri.org/"><projectId>fbdc1ed6-9d0f-4dbe-b7b2-6421edc61bcc</projectId></GetContract></s:Body></s:Envelope>
class ContractRetriever(BaseRetriever):
    def __init__(self):
        super(ContractRetriever, self).__init__("http://www.scetia.com/Scetia.SampleManage.WCF/Contract.svc",
                                                "http://tempuri.org/IContract/",
                                                "GetContract")

    def retrieve(self, project_id=None):
        rep = super(ContractRetriever, self).retrieve(projectId=project_id)
        return rep.rep_code, rep.get_response_entities("GetContractResult")


# http://www.scetia.com/Scetia.SampleManage.WCF/Sample.svc
# SOAPAction: http://tempuri.org/ISample/GtSamplesForAccountByPager
# Request: <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><GetSamplesForAccountByPager xmlns="http://tempuri.org/"><projectId>fbdc1ed6-9d0f-4dbe-b7b2-6421edc61bcc</projectId><contractSignNumber>2016004481</contractSignNumber><queryStr></queryStr><pageSize>19</pageSize><pageNum>1</pageNum></GetSamplesForAccountByPager></s:Body></s:Envelope>
class SampleRetriever(BaseRetriever):
    def __init__(self):
        super(SampleRetriever, self).__init__("http://www.scetia.com/Scetia.SampleManage.WCF/Sample.svc",
                                              "http://tempuri.org/ISample/",
                                              "GetSamplesForAccountByPager")

    def retrieve(self, project_id=None, contract_sign_number=None, query_str='', page_num=1, page_size=20):
        rep = super(SampleRetriever, self).retrieve(projectId=project_id,
                                                     contractSignNumber=contract_sign_number,
                                                     queryStr=query_str,
                                                     pageNum=page_num,
                                                     pageSize=page_size,
                                                     __order_list=["projectId", "contractSignNumber", "queryStr",
                                                                   "pageSize", "pageNum"])
        return rep.rep_code, rep.get_response_entities("GetSamplesForAccountByPagerResult")


if __name__ == "__main__":
    project_id = "fbdc1ed6-9d0f-4dbe-b7b2-6421edc61bcc"
    build_unit_id = "394eb96f-e57b-4b0a-bb29-0f1fbddfaeb6"

    contract_sign_number = "2016004481"
    query_str = ""
    page_size = 20
    page_num = 1
    build_unit_user_id = "0752221a-fa3e-4211-a3b9-e1c8886edd76"
    not_finished_only = True

    # retriever = ProjectRetriever()
    # rep = retriever.retrieve(build_unit_id=build_unit_id, page_size=page_size, page_num=page_num, build_unit_user_id=build_unit_user_id, not_finished_only=not_finished_only, query_str=query_str)
    #
    # print(rep)

    retriever = ItemRetriever()
    rep = retriever.retrieve()

    print(rep)

    # retriever = ContractRetriever()
    # rep = retriever.retrieve(project_id=project_id)
    #
    # print(rep)
    #
    # retriever = SampleRetriever()
    # rep = retriever.retrieve(project_id=project_id, contract_sign_number=contract_sign_number, query_str=query_str, page_num=page_num, page_size=page_size)
    # print(rep)

