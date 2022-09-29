import json
import os
import requests
import urllib
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import traceback


class LorisAPI:
    url = ''
    uploadURL = ''
    username = ''
    password = ''
    token = ''

    upload_read = 0
    upload_total = -1

    upload_pii_read = 0
    upload_pii_total = -1

    def login(self):
        print('login has ran')
        resp = requests.post(
            url=self.url + 'login',
            json={
                'username': self.username,
                'password': self.password
            },
            verify=False
        )

        print(resp.status_code)

        login_succeeded = {}
        if resp.status_code == 405:
            login_succeeded = {'error': 'User credentials error!'}
            print('User credentials error!')
        else:
            resp_json = json.loads(resp.content.decode('ascii'))
            print(resp_json)
            if resp_json.get('error'):
                login_succeeded = {'error': resp_json.get('error')}
            else:
                self.token = resp_json.get('token')
        return login_succeeded

    def get_projects(self):
        print('get_projects has ran')
        resp = requests.get(
            url=self.url + 'projects',
            headers={'Authorization': 'Bearer %s' % self.token, 'LORIS-Overwrite': 'overwrite'},
            verify=False
        )

        json_resp = json.loads(resp.content.decode('ascii'))
        print(json_resp)
        return json_resp.get('Projects')

    def get_all_subprojects(self):
        print('get_all_subprojects has ran')
        resp = requests.get(
            url=self.url + 'subprojects',
            headers={'Authorization': 'Bearer %s' % self.token, 'LORIS-Overwrite': 'overwrite'},
            verify=False
        )

        print(resp.status_code)
        json_resp = json.loads(resp.content.decode('ascii'))
        print(json_resp)
        return json_resp.get('Subprojects')

    def get_subprojects(self, project):
        print('get_subprojects has ran')
        project = self.get_project(project)
        print(project)
        return project.get('Subprojects')

    def get_visits(self, subproject):
        print('get_visits has ran')
        resp = requests.get(
            url=self.url + 'subprojects/' + urllib.parse.quote(subproject),
            headers={'Authorization': 'Bearer %s' % self.token, 'LORIS-Overwrite': 'overwrite'},
            verify=False
        )

        print(resp.status_code)
        json_resp = json.loads(resp.content.decode('ascii'))
        print(json_resp)
        return json_resp.get('Visits')

    def get_sites(self):
        print('get_sites has ran')
        resp = requests.get(
            url=self.url + 'sites',
            headers={'Authorization': 'Bearer %s' % self.token, 'LORIS-Overwrite': 'overwrite'},
            verify=False
        )

        print(resp.status_code)
        json_resp = json.loads(resp.content.decode('ascii'))
        print (json_resp)
        sites = json_resp.get('Sites')
        return sites

    def get_project(self, project):
        print('get_project has ran')
        resp = requests.get(
            url=self.url + 'projects/' + urllib.parse.quote(project),
            headers={'Authorization': 'Bearer %s' % self.token, 'LORIS-Overwrite': 'overwrite'},
            verify=False
        )

        print(resp.status_code)
        json_resp = json.loads(resp.content.decode('ascii'))
        print(json_resp)
        return json_resp

    def get_visit(self, candid, visit, site, subproject, project):
        print('get_visit has ran')
        resp = requests.get(
            url=self.url + '/candidates/' + str(candid) + '/' + urllib.parse.quote(visit),
            headers={'Authorization': 'Bearer %s' % self.token, 'LORIS-Overwrite': 'overwrite'},
            data=json.dumps({
                "Meta": {
                    "CandID": candid,
                    "Visit": visit,
                    "Site": site,
                    "Battery": subproject,
                    "Project": project
                }
            }),
            verify=False
        )

        print(resp.status_code)
        json_resp = json.loads(resp.content.decode('ascii'))
        print(json_resp)
        return json_resp

    def start_next_stage(self, candid, visit, site, subproject, project, date):
        print('start_next_stage has ran')
        resp = requests.patch(
            url=self.url + '/candidates/' + str(candid) + '/' + urllib.parse.quote(visit),
            headers={'Authorization': 'Bearer %s' % self.token, 'LORIS-Overwrite': 'overwrite'},
            data=json.dumps({
                "CandID": candid,
                "Visit": visit,
                "Site": site,
                "Battery": subproject,
                "Project": project,
                "Stages": {
                    "Visit": {
                        "Date": date,
                        "Status": "In Progress",
                    }
                }
            }),
            verify=False
        )
        print(resp.status_code)
        print(resp.text)

    def create_candidate(self, project, dob, sex, site):
        print('create_candidate has ran')
        resp = requests.post(
            url=self.url + '/candidates/',
            headers={'Authorization': 'Bearer %s' % self.token, 'LORIS-Overwrite': 'overwrite'},
            data=json.dumps({
                "Candidate": {
                    "Project": project,
                    "DoB": dob,
                    "Sex": sex,
                    "Site": site,
                }
            }),
            verify=False
        )

        print(resp.status_code)
        json_resp = json.loads(resp.content.decode('ascii'))
        print(json_resp)
        return json_resp

    def create_visit(self, candid, visit, site, project, subproject):
        print('create_visit has ran')
        resp = requests.put(
            url=self.url + '/candidates/' + candid + '/' + visit,
            headers={'Authorization': 'Bearer %s' % self.token, 'LORIS-Overwrite': 'overwrite'},
            data=json.dumps({
                "CandID": candid,
                "Visit": visit,
                "Site": site,
                "Battery": subproject,
                "Project": project
            }),
            verify=False
        )
        print(resp.status_code)
        # json_resp = json.loads(resp.content.decode('ascii'))
        # print(json_resp)

    def get_candidate(self, candid):
        print('get_candidate has ran for: ', candid)
        resp = requests.get(
            url=self.url + '/candidates/' + candid,
            headers={'Authorization': 'Bearer %s' % self.token, 'LORIS-Overwrite': 'overwrite'},
            verify=False
        )

        print(resp.status_code)
        json_resp = json.loads(resp.content.decode('ascii'))
        print(json_resp)

        # validate candid
        if json_resp.get('error'):
            return {'error': 'DCCID is not valid.'}

        return json_resp

    def upload_callback(self, monitor):
        # Update the upload progress
        self.upload_read = monitor.bytes_read
        self.upload_total = monitor.len
        

    def upload_pii_callback(self, monitor):
        # Update the upload progress
        self.upload_pii_read = monitor.bytes_read
        self.upload_pii_total = monitor.len

    def upload_eeg(self, filename, metaData, candID, pscid, visit):
        print('upload eeg has ran')
        self.upload_read = 0
        self.upload_total = -1
        e = MultipartEncoder(
            fields={'metaData': json.dumps(metaData), 'candID': candID, 'pscid': pscid, 'visit': visit,
                    'eegFile': (os.path.basename(filename), open(filename, 'rb'), 'application/x-tar')}
        )
        m = MultipartEncoderMonitor(e, self.upload_callback)

        resp = requests.post(self.uploadURL, data=m,
                          headers={'Content-Type': m.content_type, 'Authorization': 'Bearer %s' % self.token}, verify=False)

        print(resp.status_code)
        print(resp.text)

        return resp

    def upload_pii(self, filename):
        print('upload pii has ran')
        self.upload_pii_read = 0
        self.upload_pii_total = -1
        e = MultipartEncoder(
            fields={'eegFile': (os.path.basename(filename), open(filename, 'rb'), 'application/x-tar')}
        )
        m = MultipartEncoderMonitor(e, self.upload_pii_callback)

        resp = requests.post('https://integration.hbcd.ahc.umn.edu/api/v1/eeg', data=m,
                          headers={'Content-Type': m.content_type, 'Authorization': 'Bearer %s' % self.token}, verify=False)

        print(resp.status_code)
        print(resp.text)

        return resp