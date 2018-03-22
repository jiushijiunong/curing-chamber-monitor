# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.core.management.base import BaseCommand, CommandError
from pocket_monitor.mo import samples
from pocket_monitor.db import models

logger = logging.getLogger("mo.sync.samples")


class Command(BaseCommand):
    def __init__(self):
        self.project_retriever = samples.ProjectRetriever()

    def handle(self, *args, **options):
        project_id = "fbdc1ed6-9d0f-4dbe-b7b2-6421edc61bcc"
        build_unit_id = "394eb96f-e57b-4b0a-bb29-0f1fbddfaeb6"

        contract_sign_number = "2016004481"
        query_str = ""
        page_size = 20
        page_num = 1
        build_unit_user_id = "0752221a-fa3e-4211-a3b9-e1c8886edd76"
        not_finished_only = True


        try:
            rep = self.project_retriever.retrieve(build_unit_id=build_unit_id, page_size=page_size, page_num=page_num,
                                                  build_unit_user_id=build_unit_user_id, query_str=query_str)
            for raw_data in rep["result"]["content"]:
                try:
                    project = models.Project.objects.get(instance_id=raw_data["_Id"])

                    if project.status != int(raw_data["_ProjectStatus"]):
                        origin_status = project.status
                        project.status = int(raw_data["_ProjectStatus"])
                        project.save()
                        logger.info("Update project %s set status from %d to %d."
                                    % (raw_data["_Id"], origin_status, project.status))
                except models.Project.DoesNotExist:
                    models.Project.objects.create(instance_id=raw_data["_Id"],
                                                  name=raw_data["_ProjectName"],
                                                  nature=raw_data["_ProjectNature"],
                                                  num=raw_data["_ProjectNo"],
                                                  region=raw_data["_ProjectRegion"],
                                                  address=raw_data["_ProjectAddress"],
                                                  status=raw_data["_ProjectStatus"],
                                                  create_time=raw_data["_CreateDateTime"],
                                                  last_edit_time=raw_data["_LastEditDateTime"],
                                                  build_report_num=raw_data["_BuildingReportNumber"])
                    logger.info("Add project %s to db." % raw_data["_Id"])
        except Exception, e:
            logger.error('Sync projects error: %s' % e.message)

        # retriever = ItemRetriever()
        # rep = retriever.retrieve()
        #
        # print(rep)
        #
        # retriever = ContractRetriever()
        # rep = retriever.retrieve(project_id=project_id)
        #
        # print(rep)
        # retriever = SampleRetriever()
        # rep = retriever.retrieve(project_id=project_id, contract_sign_number=contract_sign_number, query_str=query_str,
        #                          page_num=page_num, page_size=page_size)
        # print(rep)
        # retriever = AuthenticationRetriever(cookie=".ASPXANONYMOUS=pygWkW_40wEkAAAAZTQ1MWE1ZjAtZGYyYS00MTQyLTg2OGMtZTNmOTZjNjA0Mzlliuz8w0DSZ2auDyztY2rFC-J9mBs1; CNZZDATA1256789494=91758365-1521293444-%7C1521721935; ASP.NET_SessionId=bakp2g0c3du5vuyjmdcwi1f1; .TCGHLAUTH=CCCAF62AD4DEFE4CA2DD2E629E0886C12F0DC23310FA32A9DCD4012B579C9BD3205B3E89942D2A8FA05858CBD5E1AAF8C39DB249ED42DFA71CC03D9E81EE9906A7856CC8A0E02D8B72CF3781EEB6CB39A2943224FE30CA87E9CA3FAD79E570FFCE5F39398782F9765C2AD270; UM_distinctid=16234726f89943-0454dfe6f96b3e8-1d317173-125340-16234726f8a26")
        # rep = retriever.retrieve()
        # print(rep)
