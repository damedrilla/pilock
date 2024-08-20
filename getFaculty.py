def getFaculty(conn_status, uid):
    
    try:
        section = parseUser["students"][0]["section"]
        print("Section:" + section)
    except Exception:
        try:
            instructor_list = requests.get("http://152.42.167.108/api/instructors")
            inst = json.loads(instructor_list.text)
            print(inst)
            for instr in range(len(inst["instructors"])):
                uuid = inst["instructors"][instr]["tag_uid"]
                uid_no_lead = int(uuid)
                print(uid_no_lead)
                if str(id) == str(uid_no_lead):
                    isFacultysTimeNow(
                        inst["instructors"][instr]["instructor_name"], uid_no_lead
                    )
        except Exception as e:
            print("instructor: " + str(e))