# 解剖学 Spine 权重 + 全骨骼权重绘制

> 来源: `anatomical-spine-weights` (v3.0.0)

## 核心原则

Spine 骨骼权重不应是高斯的对称分布。正确分布：
```
底部 (近髋)   缓升 W≈0.3~0.4 → 上胸峰值 W≈0.85~0.90 → 颈部急降 W≈0.05
```

## ⚠️ 世界 Z 轴陷阱

Tripo 导入模型的骨骼局部 Z ≠ 身体竖向。必须始终用世界 Z 轴。

## 完整管道

```
① Auto Weights → ② vg_manager 清理 → ③ 权重绘制 → ④ FBX 导出
```

## 两种路径

| 场景 | 路径 |
|------|------|
| **分体式**（小火人标准） | body + hands + foots → vg_manager 清理 → 权重绘制 |
| **单体式**（Tripo 直接导入） | Auto Weights → vg_manager → 清空权重 → 从头绘制全部 29 组 |

## pet_Sp_Spine 解剖学权重（核心代码）

```python
z_low = z_min + z_range * 0.18
z_high = z_min + z_range * 0.83
z_peak = t_min + (t_max - t_min) * 0.38
w_peak = 0.88

for v_idx, z in torso:
    if z <= z_peak:
        t = (z - t_min) / (z_peak - t_min)
        w = 0.10 + (w_peak - 0.10) * math.sqrt(max(0, min(1, t)))
    else:
        t = (z - z_peak) / (t_max - z_peak)
        w = w_peak * (1 - max(0, min(1, t)) ** 3)
    vg.add([v_idx], max(0.0, min(1.0, w)), 'REPLACE')
```

## 全骨骼分组策略

| 骨骼组 | 参考轴 | 分配策略 |
|--------|--------|---------|
| pet_Sp_Spine | 世界 Z | 解剖学非对称曲线（18%-83%躯干） |
| pet_Sp_hips2 | 世界 Z | 指数衰减 exp(×4), 底部→35% |
| pet_Head | 世界 Z | 顶部 75%+, 平方根缓升 |
| pet_Hips | 世界 Z | 底部 25%, 倒指数衰减 |
| pet_Root | 世界 Z | 最底部 10%, 平方衰减 |
| pet_Upper/LowerLeg_{L/R} | 世界 Z+X | X 区分左右, Z 下半部分 |
| pet_Foot/Sp_foot/Toes_{L/R} | 世界 Z+X | Z 底部逐层 |
| pet_Shoulder/UpperArm/LowerArm/Hand_{L/R} | 世界 X | X 距中心距离逐层 |
| pet_Eye_{R/L} | 世界 X+Y | 头部 Y 正面 + X 区分 |
| pet_Mouth | 世界 X+Y | 面部中心 Y 正面 |
| pet_Sp_Hair1/2 | 世界 Z | 顶部 80%+/90%+ |

## 分体式 limbs 权重镜像修复

foots/hands 只有左侧有权重时，用 L→R 几何镜像；R→L 变体直接复制权重值。

## 归一化后小骨骼组可能丢失

解剖学权重 + 归一化后 pet_Hips/pet_Spine/pet_Mouth 可能被淹没到 0 顶点。单独重新分配，不做二次全局归一化。
