def get_info(self, ret: bool):
    response = self._session.get(
        f"{self._instance_data.sirix_uri}/?withResources=true",
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Accept": "application/json",
        },
    )
    if response.status_code == 200:
        self._instance_data.database_info = response.json()["databases"]
    else:
        print(response)
    if ret:
        return self._instance_data.database_info


def create_database(self, db_name, db_type):
    response = self._session.post(
        f"{self._instance_data.sirix_uri}/{db_name}",
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Accept": "application/json" if db_type == "json" else "application/xml",
        },
    )
    if response.status_code == 200:
        # refresh database_info
        get_info(self, False)
        return True
    else:
        print(response)
        return False


def create_resource(self, data):
    data_type = (
        "application/json" if self.database_type == "json" else "application/xml"
    )
    return self._session.put(
        f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
        data=data,
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Content-Type": data_type,
            "Accept": data_type,
        },
    )


def update_resource(self, nodeId: int, data: str, insert="asFirstChild") -> bool:
    # prepare to get ETag
    params = {"nodeId": nodeId}
    data_type = (
        "application/json" if self.database_type == "json" else "application/xml"
    )
    # get ETag
    response = self._session.head(
        f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
        params=params,
        headers={"Authorization": f"Bearer {self._auth_data.access_token}"},
    )
    etag = response.headers.get("ETag")
    # prepare to update
    params.update({"insert": insert})
    # update
    response = self._session.post(
        f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
        params=params,
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Content-Type": data_type,
        },
        data=data,
    )
    if response.status_code == 201:
        return True
    return False
