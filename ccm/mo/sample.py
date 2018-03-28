# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import traceback
import time
try:
    import xml.etree.cElementTree as ele_tree
except ImportError:
    import xml.etree.ElementTree as ele_tree
from collections import OrderedDict
from _elementtree import ParseError
from _socket import timeout
from httplib import HTTPException
import logging

from ccm.common import utils, http
from ccm.ccmapp import models

logger = logging.getLogger("mo.samples")


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


class SoapResponse(object):
    def __init__(self, rep_code=None, rep_content=None):
        self.rep_code = rep_code
        self.rep_content = rep_content

    def get_response_entities(self, entity_root_name, page_count_pro_name=None, record_count_pro_name=None):
        if not self.rep_content:
            return {"content": []}
        try:
            root = ele_tree.fromstring(self.rep_content)

            # find entity root
            parent, entity_root = self._match_child_node(root, entity_root_name, True)
            if entity_root is None:
                return

            ls_ret = []
            page_info = {}
            if self._has_child(entity_root):
                for child in entity_root:
                    if self._has_child(child):
                        ret = self._get_entity(child)
                        if ret:
                            ls_ret.append(ret)
                    else:
                        ret = self._get_entity(entity_root)
                        if ret:
                            ls_ret.append(ret)
                        break
                if page_count_pro_name is not None:
                    parent, page_count = self._match_child_node(parent, page_count_pro_name)
                    if page_count.text:
                        page_info["page_count"] = int(page_count.text)
                if record_count_pro_name is not None:
                    parent, record_count = self._match_child_node(parent, record_count_pro_name)
                    if record_count.text:
                        page_info["record_count"] = int(record_count.text)
            elif entity_root.text is not None:
                ls_ret.append(entity_root.text)

            ret = {"content": ls_ret}
            if page_info:
                ret["page_info"] = page_info
            return ret
        except Exception as e:
            exstr = traceback.format_exc()
            logger.error('Parse soap response [%s] error: %s %s' % (self.rep_content, type(e), exstr))
            raise e

    def _has_child(self, node):
        for child in node:
            return True
        return False

    def _get_entity(self, node):
        ret = OrderedDict()
        for child in node:
            child_name = self._get_node_tag_name(child)
            if self._has_child(child):
                ret[child_name] = self._get_entity(child)
            else:
                ret[child_name] = child.text
        return ret

    def _get_node_tag_name(self, node):
        arr = node.tag.split("}")
        return arr[-1].split(":")[-1]

    def _match_child_node(self, node, child_node_name, recursive=False):
        for child in node:
            if self._get_node_tag_name(child) == child_node_name:
                return node, child
            else:
                if recursive:
                    return self._match_child_node(child, child_node_name, recursive)


class BaseRetriever(object):
    def __init__(self, location=None, action=None, method=None, cookie=None):
        self.req = SoapRequest(location=location, action=action, method=method)
        self.headers = {
            'Content-type': 'text/xml; charset="UTF-8"',
            'Accept-Language': 'zh-CN',
            'Connection': 'Keep-Alive',
            'Host': 'www.scetia.com',
            'DNT': 1,
            'Cache-Control': 'no-cache',
            'SOAPAction': self.req.action + self.req.method
        }
        if cookie is not None:
            self.headers['Cookie'] = cookie

    @utils.retry((HTTPException, timeout, IOError, ParseError), tries=3, logger=logger)
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

    def retrieve(self, build_unit_id=None, build_unit_user_id=None, not_finished_only=None, query_str='', page_num=1,
                 page_size=20):
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

    def retrieve(self, project_id=None, contract_sign_number=None, query_str='', page_num=1,
                 page_size=20):
        rep = super(SampleRetriever, self).retrieve(projectId=project_id,
                                                    contractSignNumber=contract_sign_number,
                                                    queryStr=query_str,
                                                    pageNum=page_num,
                                                    pageSize=page_size,
                                                    __order_list=["projectId", "contractSignNumber", "queryStr",
                                                                  "pageSize", "pageNum"])
        return {"code": rep.rep_code,
                "result": rep.get_response_entities("GetSamplesForAccountByPagerResult", "pageCount", "recordCount")}


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
        self.sample_retriever = SampleRetriever()

    def sync(self):
        start_time = time.time()
        logger.info("Sync %Ld started." % start_time)
        user_instance_id = "0752221a-fa3e-4211-a3b9-e1c8886edd76"
        build_unit_id = "394eb96f-e57b-4b0a-bb29-0f1fbddfaeb6"
        self._projects_sync(user_instance_id, build_unit_id)
        logger.info("Sync %Ld ended, cost %Ld\n\n" % (start_time, time.time() - start_time))

    def samples_count(self, user_instance_id, build_unit_id):
        logger.info("Check samples count for build unit %s of user %s" % (build_unit_id, user_instance_id))
        retrieved_samples_count = 0
        samples_count = 0
        retrieved_projects_count = 0
        projects_count = 0
        retrieved_contracts_count = 0
        contracts_count = 0
        projects = models.Project.objects.\
            filter(user_instance_id=user_instance_id, build_unit_id=build_unit_id).values("id")
        projects_count = len(projects)
        for project in projects:
            contracts = models.Contract.objects.filter(project_id=project["id"]).values("id")
            contracts_count += len(contracts)
            for contract in contracts:
                samples_count += models.Sample.objects.filter(contract_id=contract["id"]).values("id").count()
        rep = self.project_retriever.retrieve(build_unit_id=build_unit_id,
                                              page_num=1,
                                              page_size=2000,
                                              build_unit_user_id=user_instance_id)
        projects = rep["result"]["content"]
        retrieved_projects_count = len(projects)
        logger.info("Retrieved projects count %d and %d in DB for build unit %s of user %s"
                    % (retrieved_projects_count, projects_count, build_unit_id, user_instance_id))
        for project in projects:
            rep = self.contract_retriever.retrieve(project_id=project["_Id"])
            contracts = rep["result"]["content"]
            retrieved_contracts_count += len(contracts)
            for contract in contracts:
                rep = self.sample_retriever.retrieve(project_id=project["_Id"],
                                                     contract_sign_number=contract["_ContractSignNumber"],
                                                     page_num=1,
                                                     page_size=20)
                retrieved_samples_count += rep["result"]["page_info"]["record_count"]
        logger.info("Retrieved contracts count %d and %d in DB for build unit %s of user %s"
                    % (retrieved_contracts_count, contracts_count, build_unit_id, user_instance_id))
        logger.info("Retrieved samples count %d and %d in DB for build unit %s of user %s"
                    % (retrieved_samples_count, samples_count, build_unit_id, user_instance_id))

    def _projects_sync(self, user_instance_id, build_unit_id):
        current_page = 1
        logger.info("Sync for build unit %s of user %s" % (build_unit_id, user_instance_id))
        try:
            rep = self.project_retriever.retrieve(build_unit_id=build_unit_id,
                                                  page_num=current_page,
                                                  page_size=600,
                                                  build_unit_user_id=user_instance_id)
            self._do_projects_sync(rep["result"]["content"], user_instance_id, build_unit_id)
            if "page_info" in rep["result"] and "page_count" in rep["result"]["page_info"]:
                page_count = rep["result"]["page_info"]["page_count"]
                left_pages = page_count - 1
                while left_pages > 1:
                    current_page += 1
                    rep = self.project_retriever.retrieve(build_unit_id=build_unit_id,
                                                          page_num=current_page,
                                                          page_size=600,
                                                          build_unit_user_id=user_instance_id)
                    self._do_projects_sync(rep["result"]["content"], user_instance_id, build_unit_id)
                    left_pages -= 1
                    current_page += 1
        except Exception as e:
            exstr = traceback.format_exc()
            logger.error('Sync page %d of projects error for user %s: %s %s' % (current_page, user_instance_id,
                                                                                type(e), exstr))

    def _do_projects_sync(self, raw_data, user_instance_id, build_unit_id):
        pre_project_status = 0
        for project_item in raw_data:
            try:
                project = models.Project.objects.get(instance_id=project_item["_Id"])
                pre_project_status = project.status
                if project.status != int(project_item["_ProjectStatus"]):
                    project.status = int(project_item["_ProjectStatus"])
                    project.save()
                    logger.info("Update project %s set status from %d to %d."
                                % (project_item["_Id"], pre_project_status, project.status))
            except models.Project.DoesNotExist:
                project = models.Project.objects.create(instance_id=project_item["_Id"],
                                                        name=project_item["_ProjectName"],
                                                        nature=project_item["_ProjectNature"],
                                                        num=project_item["_ProjectNo"],
                                                        region=project_item["_ProjectRegion"],
                                                        address=project_item["_ProjectAddress"],
                                                        status=project_item["_ProjectStatus"],
                                                        create_time=project_item["_CreateDateTime"],
                                                        last_edit_time=project_item["_LastEditDateTime"],
                                                        building_report_num=project_item["_BuildingReportNumber"],
                                                        supervise_unit_id=project_item["_SuperviseUnitId"],
                                                        build_unit_id=build_unit_id,
                                                        user_instance_id=user_instance_id)
                logger.info("Add project %s to db for user %s." % (project_item["_Id"], user_instance_id))
            # only sync contracts for the in-progress project
            if pre_project_status == 0:
                self._contracts_sync(project)

    def _contracts_sync(self, project):
        try:
            rep = self.contract_retriever.retrieve(project_id=project.instance_id)
            self._do_contracts_sync(project, rep["result"]["content"])
        except Exception as e:
            exstr = traceback.format_exc()
            logger.error('Sync contracts error for project %s: %s %s' % (project.instance_id, type(e), exstr))

    def _do_contracts_sync(self, project, raw_data):
        for contract_item in raw_data:
            try:
                contract = models.Contract.objects.get(sign_number=contract_item["_ContractSignNumber"])
            except models.Contract.DoesNotExist:
                contract = models.Contract.objects.create(sign_number=contract_item["_ContractSignNumber"],
                                                          serial_num=contract_item["_ContractSerialNumber"],
                                                          project=project,
                                                          build_unit_id=contract_item["_BuildUnitID"],
                                                          build_unit_name=contract_item["_BuildUnitName"],
                                                          building_report_num=contract_item["_BuildingReportNumber"],
                                                          checked_date_time=contract_item["_CheckedDateTime"],
                                                          checked=bool(contract_item["_Checked"]),
                                                          detection_unit_member_code=contract_item[
                                                              "_DetectionUnitMemberCode"],
                                                          detection_unit_member_name=contract_item[
                                                              "_DetectionUnitName"],
                                                          supervise_unit_id=contract_item["_SuperviseUnitID"],
                                                          supervise_unit_name=contract_item["_SuperviseUnitName"],
                                                          manage_unit_id=contract_item["_ManageUnitID"],
                                                          manage_unit_name=contract_item["_ManageUnitName"],
                                                          entrust_unit_name=contract_item["_EntrustUnitName"],
                                                          construct_unit_name=contract_item["_ConstructUnitName"])
                logger.info("Add contract %s for project %s to db." % (contract_item["_ContractSignNumber"],
                                                                       project.instance_id))
            self._samples_sync(project, contract)

    def _samples_sync(self, project, contract):
        current_page = 1
        try:
            rep = self.sample_retriever.retrieve(project_id=project.instance_id,
                                                 contract_sign_number=contract.sign_number,
                                                 page_num=current_page,
                                                 page_size=600)
            self._do_samples_sync(contract, rep["result"]["content"])
            if "page_info" in rep["result"] and "page_count" in rep["result"]["page_info"]:
                page_count = rep["result"]["page_info"]["page_count"]
                left_pages = page_count - 1
                while left_pages > 1:
                    current_page += 1
                    rep = self.sample_retriever.retrieve(project_id=project.instance_id,
                                                         contract_sign_number=contract.sign_number,
                                                         page_num=current_page,
                                                         page_size=600)
                    self._do_samples_sync(contract, rep["result"]["content"])
                    left_pages -= 1
                    current_page += 1
        except Exception as e:
            exstr = traceback.format_exc()
            logger.error('Sync page %d of samples error for project %s contract %s: %s %s' % (current_page,
                                                                                              project.instance_id,
                                                                                              contract.sign_number,
                                                                                              type(e), exstr))

    def _do_samples_sync(self, contract, raw_data):
        for sample_item in raw_data:
            try:
                sample = models.Sample.objects.get(instance_id=sample_item["_Id"])
                pre_project_status = sample.status
                if sample.status != int(sample_item["_Sample_Status"]):
                    sample.status = int(sample_item["_Sample_Status"])
                    sample.status_str = sample_item["_SampleStatusStr"]
                    sample.save()
                    logger.info("Update sample %s set status from %d to %d."
                                % (sample_item["_Id"], pre_project_status, sample.status))
            except models.Sample.DoesNotExist:
                sample = models.Sample.objects.create(instance_id=sample_item["_Id"],
                                                      name=sample_item["_SampleName"],
                                                      num=sample_item["_SampleNo"],
                                                      item_id=sample_item["_ItemID"],
                                                      item_name=sample_item["_ItemName"],
                                                      # project=project,
                                                      contract=contract,
                                                      count=sample_item["_SampleCount"],
                                                      status=sample_item["_Sample_Status"],
                                                      status_str=sample_item["_SampleStatusStr"],
                                                      regular=bool(sample_item["_Sample_Regular"]),
                                                      kind_id=sample_item["_KindID"],
                                                      kind_name=sample_item["_KindName"],
                                                      detection_unit_member_name=sample_item["_MemberCode"],
                                                      report_num=sample_item["_ReportNumber"],
                                                      core_code_id=sample_item["_CoreCodeId"],
                                                      core_code_id_end=sample_item["_CoreCodeIdEnd"],
                                                      project_part=sample_item["_ProJect_Part"],
                                                      spec=sample_item["_SpecName"],
                                                      grade=sample_item["_GradeName"],
                                                      exam_result=sample_item["_Exam_Result"],
                                                      hnt_yhtj=sample_item["_Hnt_YHTJ"],
                                                      age_time_str=sample_item["_AgeTimeStr"],
                                                      report_date_str=sample_item["_ReportDateStr"],
                                                      detection_date_str=sample_item["_DetectionDateStr"],
                                                      molding_date_str=sample_item["_MoldingDateStr"]
                                                      )
