# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from soap_request import SoapRequest
from soap_response import SoapResponse
import pocket_monitor.http as http
from pocket_monitor.db import models
import logging

logger = logging.getLogger("mo.samples")


class BaseRetriever(object):
    def __init__(self, location=None, action=None, method=None, cookie=None):
        self.req = SoapRequest(location=location, action=action, method=method)
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
        if cookie is not None:
            self.headers['Cookie'] = cookie

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
        super(ItemRetriever, self).__init__(location="http://www.scetia.com/Scetia.SampleManage.WCF/Item.svc",
                                            action="http://tempuri.org/IItem/",
                                            method="GetItemSeries")

    def retrieve(self):
        rep = super(ItemRetriever, self).retrieve()
        return {"code": rep.rep_code, "result": rep.get_response_entities("GetItemSeriesResult")}


# http://www.scetia.com/Scetia.SampleManage.WCF/Project.svc
# SOAPAction: http://tempuri.org/IProject/GetProjectsForBuildUnit
# Request: <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><GetProjectsForBuildUnit xmlns="http://tempuri.org/"><buildUnitId>394eb96f-e57b-4b0a-bb29-0f1fbddfaeb6</buildUnitId><pageSize>20</pageSize><pageNum>1</pageNum><buildUnitUserId>0752221a-fa3e-4211-a3b9-e1c8886edd76</buildUnitUserId><queryStr xsi:nil="true" /><notFinishedOnly>true</notFinishedOnly></GetProjectsForBuildUnit></s:Body></s:Envelope>
class ProjectRetriever(BaseRetriever):
    def __init__(self):
        super(ProjectRetriever, self).__init__(location="http://www.scetia.com/Scetia.SampleManage.WCF/Project.svc",
                                               action="http://tempuri.org/IProject/",
                                               method="GetProjectsForBuildUnit")

    def retrieve(self, build_unit_id=None, build_unit_user_id=None,
                 not_finished_only=None, query_str='', page_num=1, page_size=20):
        rep = super(ProjectRetriever, self).retrieve(buildUnitId=build_unit_id,
                                                     queryStr=query_str,
                                                     buildUnitUserId=build_unit_user_id,
                                                     notFinishedOnly=not_finished_only,
                                                     pageNum=page_num,
                                                     pageSize=page_size,
                                                     __order_list=["buildUnitId", "pageSize", "pageNum",
                                                                   "buildUnitUserId", "queryStr", "notFinishedOnly"])
        return {"code": rep.rep_code, "result": rep.get_response_entities("GetProjectsForBuildUnitResult", "pageCount")}


# http://www.scetia.com/Scetia.SampleManage.WCF/Contract.svc
# SOAPAction: http://tempuri.org/IContract/GetContract
# Request: <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><GetContract xmlns="http://tempuri.org/"><projectId>fbdc1ed6-9d0f-4dbe-b7b2-6421edc61bcc</projectId></GetContract></s:Body></s:Envelope>
class ContractRetriever(BaseRetriever):
    def __init__(self):
        super(ContractRetriever, self).__init__(location="http://www.scetia.com/Scetia.SampleManage.WCF/Contract.svc",
                                                action="http://tempuri.org/IContract/",
                                                method="GetContract")

    def retrieve(self, project_id=None):
        rep = super(ContractRetriever, self).retrieve(projectId=project_id)
        return {"code": rep.rep_code, "result": rep.get_response_entities("GetContractResult")}


# http://www.scetia.com/Scetia.SampleManage.WCF/Sample.svc
# SOAPAction: http://tempuri.org/ISample/GetSamplesForAccountByPager
# Request: <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><GetSamplesForAccountByPager xmlns="http://tempuri.org/"><projectId>fbdc1ed6-9d0f-4dbe-b7b2-6421edc61bcc</projectId><contractSignNumber>2016004481</contractSignNumber><queryStr></queryStr><pageSize>19</pageSize><pageNum>1</pageNum></GetSamplesForAccountByPager></s:Body></s:Envelope>
class SampleRetriever(BaseRetriever):
    def __init__(self):
        super(SampleRetriever, self).__init__(location="http://www.scetia.com/Scetia.SampleManage.WCF/Sample.svc",
                                              action="http://tempuri.org/ISample/",
                                              method="GetSamplesForAccountByPager")

    def retrieve(self, project_id=None, contract_sign_number=None, query_str='', page_num=1, page_size=20):
        rep = super(SampleRetriever, self).retrieve(projectId=project_id,
                                                    contractSignNumber=contract_sign_number,
                                                    queryStr=query_str,
                                                    pageNum=page_num,
                                                    pageSize=page_size,
                                                    __order_list=["projectId", "contractSignNumber", "queryStr",
                                                                  "pageSize", "pageNum"])
        return {"code": rep.rep_code, "result": rep.get_response_entities("GetSamplesForAccountByPagerResult", "pageCount", "recordCount")}


# http://www.scetia.com/Scetia.OnlineExplorer/Authentication.svc
# SOAPAction: http://tempuri.org/IAuthentication/GetLoginInfo
# Request: ﻿<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><GetLoginInfo xmlns="http://tempuri.org/" /></s:Body></s:Envelope>
class AuthenticationRetriever(BaseRetriever):
    def __init__(self, cookie=None):
        super(AuthenticationRetriever, self).__init__(
            location="http://www.scetia.com/Scetia.OnlineExplorer/Authentication.svc",
            action="http://tempuri.org/IAuthentication/",
            method="GetLoginInfo",
            cookie=cookie)

    def retrieve(self):
        rep = super(AuthenticationRetriever, self).retrieve()
        return {"code": rep.rep_code, "result": rep.get_response_entities("GetLoginInfoResult")}


 # project_id = "fbdc1ed6-9d0f-4dbe-b7b2-6421edc61bcc"
 #        build_unit_id = "394eb96f-e57b-4b0a-bb29-0f1fbddfaeb6"
 #
 #        contract_sign_number = "2016004481"
 #        query_str = ""
 #        page_size = 20
 #        page_num = 1
 #        build_unit_user_id = "0752221a-fa3e-4211-a3b9-e1c8886edd76"
 #        not_finished_only = True

class Sync(object):
    def __init__(self):
        self.project_retriever = ProjectRetriever()
        self.contract_retriever = ContractRetriever()

    def sync(self):
        user_id = "0752221a-fa3e-4211-a3b9-e1c8886edd76"
        build_unit_id = "394eb96f-e57b-4b0a-bb29-0f1fbddfaeb6"
        self._projects_sync(user_id, build_unit_id)

    def _projects_sync(self, user_id=None, build_unit_id=None):
        try:
            rep = self.project_retriever.retrieve(build_unit_id=build_unit_id, page_size=20, page_num=1,
                                                  build_unit_user_id=user_id, query_str="")
            self._do_projects_sync(rep["result"]["content"])
            if "page_info" in rep["result"] and "page_count" in rep["result"]["page_info"]:
                page_count = rep["result"]["page_info"]["page_count"]
                left_pages = page_count - 1
                current_page = 1
                while left_pages > 1:
                    rep = self.project_retriever.retrieve(build_unit_id=build_unit_id, page_size=current_page, page_num=20,
                                                          build_unit_user_id=user_id, query_str="")
                    self._do_projects_sync(rep["result"]["content"])
                    left_pages -= left_pages
        except Exception as e:
            logger.error('Sync projects error for user %s: %s' % (user_id, e.message))

    def _do_projects_sync(self, raw_data):
            for project_item in raw_data:
                try:
                    project = models.Project.objects.get(instance_id=project_item["_Id"])

                    if project.status != int(project_item["_ProjectStatus"]):
                        origin_status = project.status
                        project.status = int(project_item["_ProjectStatus"])
                        project.save()
                        logger.info("Update project %s set status from %d to %d."
                                    % (project_item["_Id"], origin_status, project.status))
                except models.Project.DoesNotExist:
                    models.Project.objects.create(instance_id=project_item["_Id"],
                                                  name=project_item["_ProjectName"],
                                                  nature=project_item["_ProjectNature"],
                                                  num=project_item["_ProjectNo"],
                                                  region=project_item["_ProjectRegion"],
                                                  address=project_item["_ProjectAddress"],
                                                  status=project_item["_ProjectStatus"],
                                                  create_time=project_item["_CreateDateTime"],
                                                  last_edit_time=project_item["_LastEditDateTime"],
                                                  build_report_num=project_item["_BuildingReportNumber"])
                    logger.info("Add project %s to db." % project_item["_Id"])
            # self._contracts_sync(project_item["_Id"])

    # def _contracts_sync(self, project_id=None):
    #     try:
    #         rep = self.contract_retriever.retrieve(project_id=project_id)
    #         self._do_contracts_sync(rep["result"]["content"])
    #     except Exception as e:
    #         logger.error('Sync contracts error for project %s: %s' % (project_id, e.message))
    #
    # def _do_contracts_sync(self, raw_data):
    #     for contract_item in raw_data:
    #         try:
    #             contract = models.Contract.objects.get(instance_id=contract_item["_Id"])
    #         except models.Contract.DoesNotExist:
    #             models.Contract.objects.create(instance_id=contract_item["_Id"],
    #                                           name=project_item["_ProjectName"],
    #                                           nature=project_item["_ProjectNature"],
    #                                           num=project_item["_ProjectNo"],
    #                                           region=project_item["_ProjectRegion"],
    #                                           address=project_item["_ProjectAddress"],
    #                                           status=project_item["_ProjectStatus"],
    #                                           create_time=project_item["_CreateDateTime"],
    #                                           last_edit_time=project_item["_LastEditDateTime"],
    #                                           build_report_num=project_item["_BuildingReportNumber"])
    #             logger.info("Add contract %s to db." % contract_item["_Id"])
