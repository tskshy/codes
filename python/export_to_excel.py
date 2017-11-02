# -*- coding: utf-8 -*-

# pandas操作excel需要依赖其他库，根据提示进行安装
import pandas as pd
import pymysql


MYSQL_CONF = {
    "host":"192.168.59.8",
    "port":3306,
    "user":"test001",
    "password":"test001",
    "db":"intelligent_server",
    "charset":"utf8"
}


def get_mysql_conn():
    conn = pymysql.connect(
        host=MYSQL_CONF["host"],
        port=MYSQL_CONF["port"],
        user=MYSQL_CONF["user"],
        password=MYSQL_CONF["password"],
        db=MYSQL_CONF["db"],
        charset=MYSQL_CONF["charset"]
    )

    return conn


def export(tid):
    """
    :param tid: number
    :return:
    """
    conn = get_mysql_conn()
    with conn.cursor() as cursor:
        # 主问题和相似问题可以一行查询出来，但是，由于相似问题中存在特殊字符，无法很好的进行解析
        sql = """
select
	c.tenant_id,
	c.main_id,
	c.`type`,
	c.content_type,
	c.main_question,
	c.like_question,
	c.answer,
	(
		select
			category_name
		from
			qa_category
		where
			id = c.category_id
	) as category_name
from
	(
		select
			a.tenant_id as tenant_id,
			a.id as main_id,
			a.question as main_question,
			b.question as like_question,
			a.answer as answer,
			a.content_type as content_type,
			a.`type` as `type`,
			a.category_id as category_id
		from
			main_question a left join like_question b on
			a.id = b.main_id
			and b.is_verify = 1
			and b.is_delete = 0
		where
			a.tenant_id = {0}
			and a.is_verify = 1
			and a.is_delete = 0
		order by
			main_id
	) c
	        """.format(tid)

        cursor.execute(sql)
        res = cursor.fetchall()

        d = dict()
        for item in res:
            tenant_id = item[0]
            main_id = item[1]
            _type = item[2]
            content_type = item[3]
            main_question = item[4]
            like_question = item[5]
            answer = item[6]
            category_name = item[7]

            if content_type == "text":
                file_name = "tenantid_{0}_type_{1}.xlsx".format(tenant_id, _type)
                if d.get(file_name) is None:
                    d[file_name] = dict()
                    d[file_name]["columns"] = ["标准问题", "相似问题1", "相似问题2", "相似问题3", "标准答案", "一级问题分类"]

                if d[file_name].get(main_id) is None:
                    d[file_name][main_id] = [main_question, "" if like_question is None else like_question, "", "", answer, category_name]
                else:
                    info = d[file_name][main_id]
                    # 保证前面的格式
                    if info[2] == "":
                        #d[file_name][main_id][2] = like_question
                        info[2] = like_question
                    elif info[3] == "":
                        #d[file_name][main_id][3] = like_question
                        info[3] = like_question
                    else:
                        info.append(like_question)
                        for i in range(len(info) - len(d[file_name]["columns"])):
                            d[file_name]["columns"].append("相似问题{0}".format(len(d[file_name]["columns"]) - 2))
            else:
                file_name = "tenantid_{0}.xlsx".format(tenant_id,)
                if d.get(file_name) is None:
                    d[file_name] = dict()
                    d[file_name]["columns"] = ["tenantid", "type", "mainid", "question", "like_question"]

                if d[file_name].get(main_id) is None:
                    d[file_name][main_id] = [tenant_id, _type, main_id, main_question, "" if like_question is None else like_question]
                else:
                    info = d[file_name][main_id]
                    info.append(like_question)
                    for i in range(len(info) - len(d[file_name]["columns"])):
                        d[file_name]["columns"].append("like_question")


        for file_name in d:
            columns = d[file_name]["columns"]
            lst = list()

            for key in d[file_name]:
                if key == "columns":
                    continue

                lst.append(d[file_name][key])

            writer = pd.ExcelWriter(file_name)

            df = pd.DataFrame(data=lst, columns=columns)
            df.to_excel(writer, "qas", header=True, index=False)
            writer.save()
    conn.close()


def read_test():
    path = "/root/Downloads/model_test.xlsx"
    d = pd.read_excel(path, sheetname="qas")
    print(d["标准问题"])

def write_test():
    path = "/root/Downloads/model_test.xlsx"
    writer = pd.ExcelWriter(path)

    df = pd.DataFrame(data=[[1,2,1,2,1,2],[4,5,4,5,4,5],[4,5,4,5,4,5]], columns=["标准问题", "相似问题1", "相似问题2", "相似问题3", "标准答案", "一级问题分类"])
    df.to_excel(writer, "qas", header=True, index=False)
    writer.save()




if __name__ == "__main__":
    export(8)
    pass


