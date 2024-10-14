---
title: "Go项目部署+实战（二）"
subtitle: ""
date: 2024-10-13T15:33:14+08:00
lastmod: 2024-10-13T15:33:14+08:00
draft: true
author: "hxy"
authorLink: ""
license: ""
tags: ["技巧"]
categories: [""]
featuredImage: ""
featuredImagePreview: ""
summary: ""
hiddenFromHomePage: false
hiddenFromSearch: false
toc:
  enable: true
  auto: true
mapbox:
share:
  enable: true
comment:
  enable: true
---

### 多表联查的实现
谈到多表联查，有多种实现方法。比较传统的为数据库课程所教的视图方法。然而灵活性较差。
在Springboot中，采用映射表实现，而**go+gin+gorm**框架中，又有所不同。
下面笔者通过一个案例介绍多表联查的应用场景。

#### 场景概述
有一个合唱团，声部长负责批改作业。该接口需要查询声部长负责声部的所有人作业情况。
实体表有用户表、合唱团表、用户-合唱团表、作业表、作业提交表。

#### 分析
首先需要明确设计表结构，易混淆的在于**用户的角色权限**和**声部**是隶属**用户-合唱团**表，而非用户本身。
思路为，查询用户所在声部权限比他低的人。

示例代码
```go
func AdminGetHomeworks(c *gin.Context) {
	homeworkId, _ := strconv.Atoi(c.Param("homeworkId"))
	var submissions []HomeworkSubmissionInfo
	chorusLeaderID := c.GetInt("userId")
	err := config.DB.Table("homework_submission").
    Joins("JOIN homework ON homework.id = homework_submission.homework_id").
		Joins("JOIN join_chorus ON homework.chorus_id = join_chorus.chorus_id").
		Joins("JOIN user ON homework_submission.user_id = user.id and is_final = 1").
		Where("join_chorus.user_id = ? AND join_chorus.role_id = ?", chorusLeaderID, 3).
		Where("homework.id = ? and homework_submission.status = ?", homeworkId, "under_review").
		Select("homework_submission.id, homework_submission.status, homework_submission.media_url, homework_submission.submit_time, user.name AS submitter_name").
		Find(&submissions).Error
	if err != nil {
		utils.JsonErrorResponse(c, err)
		return
	}
	utils.JsonSuccessResponse(c, submissions)
}
```

#### 难点
left join、right join和join的区别。
left join以左表为主，若右表没有查到，置空值。
right join反之。
join（inner join）要求严格匹配。

#### Preload的使用

在多表联查业务中，有时会出现返回的结构体中某个属性的类型为实体/实体列表。

此时，可以使用Preload简化代码。

```go
// 返回结构体
type BoardResult struct {
	ID          int                 `json:"id" gorm:"primaryKey"`
	SubmitterId int                 `json:"submitterId"`
	Submitter   string              `json:"submitter"`
	Title       string              `json:"title"`
	Desc        string              `json:"desc"`
	SubmitTime  utils.CustomTime    `json:"submitTime"`
	Images      []models.BoardImage `json:"images" gorm:"foreignKey:BoardId"`
}
// 事实上，Images的类型为BoardImage实体组成的列表。
func GetBoardById(c *gin.Context) {
	var result BoardResult
	boardId := c.Param("boardId")
	if err := config.DB.Table("board").
		Select("board.*, user.name as submitter").
		Preload("Images"). // 预加载 BoardImage
		Joins("left join board_image on board.id = board_image.board_id").
		Joins("left join user on user.id = board.submitter_id").
		Where("board.id = ?", boardId).
		Find(&result).Error; err != nil {
		// 处理错误
		log.Println("Error occurred while fetching board results with images:", err)
		fmt.Println(err)
		utils.JsonErrorResponse(c, err)
		return
	}
	utils.JsonSuccessResponse(c, result)
}
```



### 自定义时间的实现
go语言的time.Time默认返回的不是YYYY-MM-dd HH:mm:ss的类型。
因此需要自定义CustomTime和CustomDate类，分别对应mysql datetime和date类型。

下面笔者以CustomTime为例。需要重写Scan、Value、MarshalJson、UnmarshalJson四个方法。
```go
// 自定义时间类型
type CustomTime struct {
	time.Time
}

// 实现 sql.Scanner 接口：将数据库的时间数据扫描到 CustomTime 类型中
func (ct *CustomTime) Scan(value interface{}) error {
	if t, ok := value.(time.Time); ok {
		*ct = CustomTime{Time: t}
		return nil
	}
	return fmt.Errorf("unsupported Scan, storing driver.Value type %T into type CustomTime", value)
}

// 实现 driver.Valuer 接口：将 CustomTime 类型的数据存储到数据库中
func (ct CustomTime) Value() (driver.Value, error) {
	return ct.Time, nil
}

// 实现自定义的时间格式化输出（例如：2024-10-02 00:00:00）
func (ct CustomTime) MarshalJSON() ([]byte, error) {
	formatted := fmt.Sprintf("\"%s\"", ct.Time.Format("2006-01-02 15:04:05"))
	return []byte(formatted), nil
}

// UnmarshalJSON 自定义 JSON 解析格式
func (ct *CustomTime) UnmarshalJSON(data []byte) error {
	// 解析字符串，去掉引号
	var dateString string
	if err := json.Unmarshal(data, &dateString); err != nil {
		return err
	}
	// 解析为 time.Time
	t, err := time.Parse("2006-01-02 00:00:00", dateString)
	if err != nil {
		return err
	}
	ct.Time = t
	return nil
}
```
至此，完成完整的CustomTime类封装。感兴趣可以自行尝试CustomDate的封装。

### gin框架接收ajax请求
- GET 请求

```go
c.Query("") //获取query参数
c.Param("") //获取path参数
```



- POST 请求

```go
c.shouldBindJson(&postForm) //获取json
c.PostForm() // 获取form-data格式
c.FormFile("file") //接收文件
```



### 发送ajax请求
相比java而言，go发送请求更加简单。使用"net/http"库
- GET请求
```go
resp, _ := http.Get(url)
body, _ := io.ReadAll(resp.Body)
if err := json.Unmarshal(body, &result); err != nil {
	return result, err
}
```
- POST请求

  - json

  ```go
  jsonData := map[string]interface{}{
  	"key1": "value1",
      "key2": "value2",
  }
  // 发送 HTTP 请求到微信 API
  body, _ := json.Marshal(jsonData)
  req, _ := http.NewRequest("POST", url, bytes.NewBuffer(body))
  req.Header.Set("Content-Type", "application/json")
  client := &http.Client{}
  resp, err := client.Do(req)
  fmt.Println(resp)
  if err != nil {
  	return err
  }
  defer resp.Body.Close()
  // 读取响应内容
  if body, err = ioutil.ReadAll(resp.Body); err != nil {
  	fmt.Println("Error reading response body:", err)
  	return err
  }
  ```

  - form-data

  ```go
  formData := url.Values{
      "key1": {"value1"},
      "key2": {"value2"},
  }
  // 发送 POST 请求
  resp, err := http.PostForm("https://example.com/api", formData)
  if err != nil {
      fmt.Println("Error:", err)
      return
  }
  defer resp.Body.Close() // 读取响应
  if body, err := ioutil.ReadAll(resp.Body); err != nil {
      fmt.Println("Error reading response body:", err)
      return
  }
  ```

  