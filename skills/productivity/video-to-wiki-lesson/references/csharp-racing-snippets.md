# Unity 赛车游戏常用代码片段

从 Mario Kart Unity 6 课程中提取的可复用代码模式。

## Kart Splat — 车辆压扁

障碍物撞击车辆时的压扁效果：

```csharp
void OnCollisionEnter(Collision collision) {
    if (collision.gameObject.CompareTag("Player")) {
        // 将车辆 Scale Y 压扁
        collision.transform.localScale = new Vector3(1, 0.2f, 1);
        splatSound.Play();
        StartCoroutine(ResetKart(collision.gameObject));
    }
}

IEnumerator ResetKart(GameObject kart) {
    yield return new WaitForSeconds(1.5f);
    kart.transform.localScale = Vector3.one;  // 恢复
}
```

## AI Waypoint 导航

```csharp
public class AICartControl : MonoBehaviour {
    public Transform[] waypoints;
    private int currentWaypoint = 0;

    void Update() {
        Transform target = waypoints[currentWaypoint];
        Vector3 direction = target.position - transform.position;
        
        // 计算转向（SignedAngle 自动处理左右）
        float angle = Vector3.SignedAngle(transform.forward, direction, Vector3.up);
        Vector2 steering = new Vector2(Mathf.Clamp(angle / 45f, -1, 1), 0);
        
        // 接近目标时切换
        float dist = Vector3.Distance(transform.position, target.position);
        if (dist < 8f) {
            currentWaypoint = (currentWaypoint + 1) % waypoints.Length;
        }
    }
}
```

## Rubber Band AI（追赶机制）

```csharp
// 根据排名动态调整 AI 速度
float speedMultiplier = 1.0f;
if (aiRank == 1)        speedMultiplier = 0.95f; // 领先者稍慢
else if (aiRank == last) speedMultiplier = 1.15f; // 落后者追赶
```

## 追踪导弹（Homing Missile）

```csharp
public class Missile : MonoBehaviour {
    public float speed = 30f;
    public float turnSpeed = 5f;
    private Transform target;

    void Update() {
        if (target == null) { FindTarget(); return; }
        Vector3 direction = (target.position - transform.position).normalized;
        Quaternion lookRotation = Quaternion.LookRotation(direction);
        transform.rotation = Quaternion.Slerp(transform.rotation, lookRotation, 
                                              turnSpeed * Time.deltaTime);
        transform.Translate(Vector3.forward * speed * Time.deltaTime);
    }
}
```

## 起跑倒计时

```csharp
IEnumerator StartCountdown() {
    yield return new WaitForSeconds(1f);
    countdownText.text = "3";  countdownSound.Play();
    yield return new WaitForSeconds(1f);
    countdownText.text = "2";  countdownSound.Play();
    yield return new WaitForSeconds(1f);
    countdownText.text = "1";  countdownSound.Play();
    yield return new WaitForSeconds(1f);
    countdownText.text = "GO!"; startSound.Play();
    GameManager.Instance.StartRace();
    yield return new WaitForSeconds(0.5f);
    countdownText.gameObject.SetActive(false);
}
```

## 车速表显示

```csharp
// m/s → mph（乘以 2.2369）
float speed = rb.linearVelocity.magnitude * 2.2369f;
speedText.text = Mathf.RoundToInt(speed).ToString();
```

## 引擎音效插值

```csharp
// 音量/音高随速度平滑变化
drivingSound.volume = Mathf.Lerp(0.0f, 1.0f, cartSpeed / 100f);
drivingSound.pitch = Mathf.Lerp(0.1f, 2.0f, cartSpeed / 100f);
```
