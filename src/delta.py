import logging

from utils.config import DELTA_URL, DELTA_AUTH_URL, DELTA_REALM, DELTA_CLIENT_ID, DELTA_CLIENT_SECRET
from utils.api_requests import APIClient
from models import Log
from database import get_session

logger = logging.getLogger(__name__)


delta_client = APIClient(DELTA_URL, auth_url=DELTA_AUTH_URL, realm=DELTA_REALM, client_id=DELTA_CLIENT_ID, client_secret=DELTA_CLIENT_SECRET)


def search(search_dict=None, user=None):
    if user:
        if search_dict:
            res = delta_client.make_request(method='POST', path='api/object/graph-query', json=search_dict)

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


def get_cpr_search(cpr, user=None, has_cpr_rights=False):
    if user and has_cpr_rights:
        db_session = get_session()
        search_log = Log(username=user["username"], email=user["email"], message=f"Searched for cpr: {cpr}")
        db_session.add(search_log)
        db_session.commit()
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
        # db_session = get_session()
        # search_log = Log(username=user["username"], email=user["email"], message=f"Searched for DQ-number: {dq_number}")
        # db_session.add(search_log)
        # db_session.commit()
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
