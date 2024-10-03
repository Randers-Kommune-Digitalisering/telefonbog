import base64
import logging
import requests_pkcs12 as requests

from config import DELTA_CERT_PASSWORD, DELTA_CERT_BASE64

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url, password=None, cert_base64=None):
        self.base_url = base_url
        self.password = password
        self.cert_data = None

        if cert_base64:
            self.cert_data = base64.b64decode(cert_base64)

        self.logger = logging.getLogger(__name__)

    def make_request(self, **kwargs):
        try:
            if self.cert_data:
                kwargs['pkcs12_data'] = self.cert_data
                kwargs['pkcs12_password'] = self.password

            if 'path' in kwargs:
                if not isinstance(kwargs['path'], str):
                    raise ValueError('Path must be a string')
                url = self.base_url.rstrip('/') + '/' + kwargs.pop('path').lstrip('/')
            else:
                url = self.base_url

            if not any(ele in kwargs for ele in ['method', 'json', 'data', 'files']):
                method_string = 'GET'
                method = requests.get
            elif 'method' in kwargs:
                method_string = kwargs.pop('method').strip().upper()
                method = getattr(requests, method_string.lower())
            else:
                method_string = 'POST'
                method = requests.post

            # if 'json' in kwargs:
            #    kwargs['headers']['Content-Type'] = 'application/json'

            response = method(url, **kwargs)
            response.raise_for_status()

            self.logger.info(f'{method_string} request to {url} successful')

            if 'application/json' in response.headers.get('Content-Type', ''):
                return response.json()
            else:
                if not response.content:
                    return b' '
                return response.content

        except Exception as e:
            self.logger.error(f'Request failed with error: {e.__class__} {e}')


delta_client = APIClient('https://delta-cert.kmd.dk/api/object', password=DELTA_CERT_PASSWORD, cert_base64=DELTA_CERT_BASE64)


def get_cpr_search(cpr, user=None, has_cpr_rights=False):
    if user and has_cpr_rights:
        logger.info(f'User {user["username"]} (email: {user["email"]}) is searching for CPR: {cpr}')
        return {
            "graphQueries": [
                {
                    "computeAvailablePages": False,
                    "graphQuery": {
                        "structure": {
                            "alias": "employee",
                            "userKey": "APOS-Types-Engagement",
                            "attributes": [
                                {
                                    "alias": "email",
                                    "userKey": "APOS-Types-Engagement-Attribute-Email"
                                },
                                {
                                    "alias": "phone",
                                    "userKey": "APOS-Types-Engagement-Attribute-Phone"
                                },
                                {
                                    "alias": "mobile",
                                    "userKey": "APOS-Types-Engagement-Attribute-Mobile"
                                }
                            ],
                            "relations": [
                                {
                                    "alias": "person",
                                    "title": "APOS-Types-Engagement-TypeRelation-Person",
                                    "userKey": "APOS-Types-Engagement-TypeRelation-Person",
                                    "typeUserKey": "APOS-Types-Person",
                                    "direction": "OUT",
                                    "relations": [
                                        {
                                            "alias": "user",
                                            "userKey": "APOS-Types-User-TypeRelation-Person",
                                            "typeUserKey": "APOS-Types-User",
                                            "direction": "IN"
                                        }
                                    ]
                                },
                                {
                                    "alias": "unit",
                                    "title": "APOS-Types-Engagement-TypeRelation-AdmUnit",
                                    "userKey": "APOS-Types-Engagement-TypeRelation-AdmUnit",
                                    "typeUserKey": "APOS-Types-AdministrativeUnit",
                                    "direction": "OUT"
                                }
                            ]
                        },
                        "criteria": {
                            "type": "AND",
                            "criteria": [
                                {
                                    "type": "MATCH",
                                    "operator": "EQUAL",
                                    "left": {
                                        "source": "DEFINITION",
                                        "alias": "employee.person.$userKey"
                                    },
                                    "right": {
                                        "source": "STATIC",
                                        "value": cpr
                                    }
                                },
                                {
                                    "type": "MATCH",
                                    "operator": "EQUAL",
                                    "left": {
                                        "source": "DEFINITION",
                                        "alias": "employee.$state"
                                    },
                                    "right": {
                                        "source": "STATIC",
                                        "value": "STATE_ACTIVE"
                                    }
                                }
                            ]
                        },
                        "projection": {
                            "identity": True,
                            "state": True,
                            "attributes": [
                                "APOS-Types-Engagement-Attribute-Mobile",
                                "APOS-Types-Engagement-Attribute-Phone",
                                "APOS-Types-Engagement-Attribute-Email"
                            ],
                            "typeRelations": [
                                    {
                                        "userKey": "APOS-Types-Engagement-TypeRelation-Person",
                                        "projection": {
                                            "state": True,
                                            "attributes": [
                                                "APOS-Types-Person-Attribute-SurnameAndName"
                                            ],
                                            "incomingTypeRelations": [
                                                {
                                                    "userKey": "APOS-Types-User-TypeRelation-Person",
                                                    "projection": {
                                                        "identity": True
                                                    }
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "userKey": "APOS-Types-Engagement-TypeRelation-AdmUnit",
                                        "projection": {
                                            "identity": True
                                        }
                                    }
                                ]
                        }
                    },
                    "validDate": "NOW",
                    "limit": 1
                }
            ]
        }


def get_dq_number_search(dq_number, user=None):
    if user:
        logger.info(f'User {user["username"]} (email: {user["email"]}) is searching for: {dq_number}')
        return {
            "graphQueries": [
                {
                    "computeAvailablePages": False,
                    "graphQuery": {
                        "structure": {
                            "alias": "employee",
                            "userKey": "APOS-Types-Engagement",
                            "attributes": [
                                {
                                    "alias": "email",
                                    "userKey": "APOS-Types-Engagement-Attribute-Email"
                                },
                                {
                                    "alias": "phone",
                                    "userKey": "APOS-Types-Engagement-Attribute-Phone"
                                },
                                {
                                    "alias": "mobile",
                                    "userKey": "APOS-Types-Engagement-Attribute-Mobile"
                                }
                            ],
                            "relations": [
                                {
                                    "alias": "person",
                                    "title": "APOS-Types-Engagement-TypeRelation-Person",
                                    "userKey": "APOS-Types-Engagement-TypeRelation-Person",
                                    "typeUserKey": "APOS-Types-Person",
                                    "direction": "OUT",
                                    "relations": [
                                        {
                                            "alias": "user",
                                            "userKey": "APOS-Types-User-TypeRelation-Person",
                                            "typeUserKey": "APOS-Types-User",
                                            "direction": "IN"
                                        }
                                    ]
                                },
                                {
                                    "alias": "unit",
                                    "title": "APOS-Types-Engagement-TypeRelation-AdmUnit",
                                    "userKey": "APOS-Types-Engagement-TypeRelation-AdmUnit",
                                    "typeUserKey": "APOS-Types-AdministrativeUnit",
                                    "direction": "OUT"
                                }
                            ]
                        },
                        "criteria": {
                            "type": "AND",
                            "criteria": [
                                {
                                    "type": "MATCH",
                                    "operator": "EQUAL",
                                    "left": {
                                        "source": "DEFINITION",
                                        "alias": "employee.person.user.$userKey"
                                    },
                                    "right": {
                                        "source": "STATIC",
                                        "value": dq_number
                                    }
                                },
                                {
                                    "type": "MATCH",
                                    "operator": "EQUAL",
                                    "left": {
                                        "source": "DEFINITION",
                                        "alias": "employee.$state"
                                    },
                                    "right": {
                                        "source": "STATIC",
                                        "value": "STATE_ACTIVE"
                                    }
                                }
                            ]
                        },
                        "projection": {
                            "identity": True,
                            "state": True,
                            "attributes": [
                                "APOS-Types-Engagement-Attribute-Mobile",
                                "APOS-Types-Engagement-Attribute-Phone",
                                "APOS-Types-Engagement-Attribute-Email"
                            ],
                            "typeRelations": [
                                    {
                                        "userKey": "APOS-Types-Engagement-TypeRelation-Person",
                                        "projection": {
                                            "state": True,
                                            "attributes": [
                                                "APOS-Types-Person-Attribute-SurnameAndName"
                                            ],
                                            "incomingTypeRelations": [
                                                {
                                                    "userKey": "APOS-Types-User-TypeRelation-Person",
                                                    "projection": {
                                                        "identity": True
                                                    }
                                                }
                                            ]
                                        }
                                    },
                                    {
                                        "userKey": "APOS-Types-Engagement-TypeRelation-AdmUnit",
                                        "projection": {
                                            "identity": True
                                        }
                                    }
                                ]
                        }
                    },
                    "validDate": "NOW",
                    "limit": 1
                }
            ]
        }

# Removed - not working as intended
# def get_general_search(query, user=None, offset=0, limit=100):
#     if user:
#         logger.info(f'User {user["username"]} (email: {user["email"]}) is searching for: {query}')
#         return {
#             "graphQueries": [
#                 {
#                     "computeAvailablePages": True,
#                     "graphQuery": {
#                         "structure": {
#                             "alias": "employee",
#                             "userKey": "APOS-Types-Engagement",
#                             "attributes": [
#                                 {
#                                     "alias": "email",
#                                     "userKey": "APOS-Types-Engagement-Attribute-Email"
#                                 },
#                                 {
#                                     "alias": "phone",
#                                     "userKey": "APOS-Types-Engagement-Attribute-Phone"
#                                 },
#                                 {
#                                     "alias": "mobile",
#                                     "userKey": "APOS-Types-Engagement-Attribute-Mobile"
#                                 }
#                             ],
#                             "relations": [
#                                 {
#                                     "alias": "person",
#                                     "title": "APOS-Types-Engagement-TypeRelation-Person",
#                                     "userKey": "APOS-Types-Engagement-TypeRelation-Person",
#                                     "typeUserKey": "APOS-Types-Person",
#                                     "direction": "OUT",
#                                     "relations": [
#                                         {
#                                             "alias": "user",
#                                             "userKey": "APOS-Types-User-TypeRelation-Person",
#                                             "typeUserKey": "APOS-Types-User",
#                                             "direction": "IN"
#                                         }
#                                     ]
#                                 },
#                                 {
#                                     "alias": "unit",
#                                     "title": "APOS-Types-Engagement-TypeRelation-AdmUnit",
#                                     "userKey": "APOS-Types-Engagement-TypeRelation-AdmUnit",
#                                     "typeUserKey": "APOS-Types-AdministrativeUnit",
#                                     "direction": "OUT"
#                                 }
#                             ]
#                         },
#                         "criteria": {
#                             "type": "OR",
#                             "criteria": [
#                                 {
#                                     "type": "MATCH",
#                                     "operator": "LIKE",
#                                     "left": {
#                                         "source": "DEFINITION",
#                                         "alias": "employee.email"
#                                     },
#                                     "right": {
#                                         "source": "STATIC",
#                                         "value": f"%{query}%"
#                                     }
#                                 },
#                                 {
#                                     "type": "MATCH",
#                                     "operator": "LIKE",
#                                     "left": {
#                                         "source": "DEFINITION",
#                                         "alias": "employee.phone"
#                                     },
#                                     "right": {
#                                         "source": "STATIC",
#                                         "value": f"%{query}%"
#                                     }
#                                 },
#                                 {
#                                     "type": "MATCH",
#                                     "operator": "LIKE",
#                                     "left": {
#                                         "source": "DEFINITION",
#                                         "alias": "employee.mobile"
#                                     },
#                                     "right": {
#                                         "source": "STATIC",
#                                         "value": f"%{query}%"
#                                     }
#                                 },
#                                 {
#                                     "type": "MATCH",
#                                     "operator": "LIKE",
#                                     "left": {
#                                         "source": "DEFINITION",
#                                         "alias": "employee.$name"
#                                     },
#                                     "right": {
#                                         "source": "STATIC",
#                                         "value": f"%{query}%"
#                                     }
#                                 }
#                             ],
#                             "type": "AND",
#                             "criteria": [
#                                 {
#                                     "type": "MATCH",
#                                     "operator": "EQUAL",
#                                     "left": {
#                                         "source": "DEFINITION",
#                                         "alias": "employee.$state"
#                                     },
#                                     "right": {
#                                         "source": "STATIC",
#                                         "value": "STATE_ACTIVE"
#                                     }
#                                 }
#                             ]
#                         },
#                         "projection": {
#                             "identity": True,
#                             "state": True,
#                             "attributes": [
#                                 "APOS-Types-Engagement-Attribute-Mobile",
#                                 "APOS-Types-Engagement-Attribute-Phone",
#                                 "APOS-Types-Engagement-Attribute-Email"
#                             ],
#                             "typeRelations": [
#                                     {
#                                         "userKey": "APOS-Types-Engagement-TypeRelation-Person",
#                                         "projection": {
#                                             "state": True,
#                                             "attributes": [
#                                                 "APOS-Types-Person-Attribute-SurnameAndName"
#                                             ],
#                                             "incomingTypeRelations": [
#                                                 {
#                                                     "userKey": "APOS-Types-User-TypeRelation-Person",
#                                                     "projection": {
#                                                         "identity": True
#                                                     }
#                                                 }
#                                             ]
#                                         }
#                                     },
#                                     {
#                                         "userKey": "APOS-Types-Engagement-TypeRelation-AdmUnit",
#                                         "projection": {
#                                             "identity": True
#                                         }
#                                     }
#                                 ]
#                         }
#                     },
#                     "validDate": "NOW",
#                     "limit": limit,
#                     "offset": offset
#                 }
#             ]
#         }


def search(search_dict=None, user=None):
    if user:
        if search_dict:
            res = delta_client.make_request(method='POST', path='graph-query', json=search_dict)

            if res:
                res = res.get('graphQueryResult', [])
            else:
                raise ValueError('Intet svar fra Delta')
            
            if len(res) > 0:
                instances = res[0].get('instances', [])
                if len(instances) < 1:
                    return None
                else:
                    people = []
                    for e in instances:
                        attributes = e.get('attributes', [])

                        email = next((item.get('value', '-') for item in attributes if item['userKey'] == 'APOS-Types-Engagement-Attribute-Email'), '-')
                        mobile = next((item.get('value', '-') for item in attributes if item['userKey'] == 'APOS-Types-Engagement-Attribute-Mobile'), '-')
                        phone = next((item.get('value', '-') for item in attributes if item['userKey'] == 'APOS-Types-Engagement-Attribute-Phone'), '-')

                        relations = e.get('typeRefs', [])
                        department = next((item.get('targetObject', {}).get('identity', {}).get('name', '-') for item in relations if item['userKey'] == 'APOS-Types-Engagement-TypeRelation-AdmUnit'), '-')
                        name = next((item.get('targetObject', {}).get('attributes', [{}])[0].get('value', '-') for item in relations if item['userKey'] == 'APOS-Types-Engagement-TypeRelation-Person'), '-')

                        incoming_type_relations = next((item.get('targetObject', {}).get('inTypeRefs', None) for item in relations if item['userKey'] == 'APOS-Types-Engagement-TypeRelation-Person'), None)
                        if incoming_type_relations:
                            user = incoming_type_relations[0].get('targetObject', {}).get('identity', {}).get('name', '-')
                        else:
                            user = '-'

                        person = {
                            'Navn': name,
                            'E-mail': email,
                            'Telefon': phone,
                            'Mobil': mobile,
                            'Afdeling': department,
                            'DQ-nummer': user
                        }

                        for key, value in person.items():
                            if not value:
                                person[key] = '-'

                        people.append(person)

                    return people
