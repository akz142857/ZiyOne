# World Model Learning Roadmap on Apple M4 Pro Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Build a three-stage, hands-on learning path for world models on an Apple M4 Pro with 64 GB unified memory, progressing from low-dimensional state prediction to image latent dynamics and finally JEPA-style latent prediction.

**Architecture:** Keep the project small, local-first, and MPS-compatible. Each stage produces a runnable demo, a short experiment report, and reusable code under `experiments/world-models/`, with no dependency on CUDA-only libraries.

**Tech Stack:** Python 3.11+, `uv`, PyTorch with Apple MPS, NumPy, Matplotlib, Gymnasium/Minigrid optional, pure Python synthetic data for the first demos.

---

## Hardware Baseline

User machine:

```text
Computer: Apple M4 Pro
Memory: 64 GB unified memory
GPU backend: Apple Metal / PyTorch MPS
```

Practical constraints:

- Good for: low-dimensional world models, small image world models, 64×64 / 96×96 latent prediction, small CNN/Transformer experiments.
- Acceptable with care: 128×128 image/video models, small JEPA-style experiments with reduced batch size.
- Not ideal for: full V-JEPA / V-JEPA 2 scale, large web-video training, CUDA-only robotics simulators, multi-GPU RL pipelines.

Default training targets:

```text
Stage 1: CPU or MPS, minutes
Stage 2: MPS, minutes to a few hours
Stage 3: MPS, a few hours for small JEPA-style runs
```

Default optimization rules:

- Start with `float32`; only try mixed precision after correctness is stable.
- Use small images first: `64×64`.
- Keep sequence length short: `3–8` frames.
- Prefer synthetic datasets before real video.
- Save every run config and metrics.

---

## Repository Layout

Create this structure:

```text
experiments/world-models/
├── README.md
├── pyproject.toml
├── src/world_models/
│   ├── __init__.py
│   ├── device.py
│   ├── datasets/
│   │   ├── __init__.py
│   │   ├── bouncing_ball.py
│   │   └── state_rollout.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── state_mlp.py
│   │   ├── cnn_autoencoder.py
│   │   ├── latent_dynamics.py
│   │   └── mini_jepa.py
│   ├── training/
│   │   ├── __init__.py
│   │   ├── train_state_model.py
│   │   ├── train_image_latent.py
│   │   └── train_mini_jepa.py
│   └── evaluation/
│       ├── __init__.py
│       ├── rollout.py
│       └── plots.py
├── tests/
│   ├── test_bouncing_ball.py
│   ├── test_state_model.py
│   ├── test_image_shapes.py
│   └── test_jepa_shapes.py
├── configs/
│   ├── stage1_state.yaml
│   ├── stage2_image_latent.yaml
│   └── stage3_mini_jepa.yaml
├── runs/.gitkeep
└── reports/
    ├── stage1.md
    ├── stage2.md
    └── stage3.md
```

---

# Stage 1 — Low-Dimensional State World Model

## Learning Objective

Understand the core world-model loop:

```text
state_t + action_t -> transition_model -> state_{t+1}
```

This stage avoids images entirely. The model learns simple dynamics from numeric state vectors.

## Demo Environment

Use a synthetic 2D bouncing ball.

State:

```text
[x, y, vx, vy]
```

Action:

```text
[ax, ay]
```

Prediction target:

```text
[x_next, y_next, vx_next, vy_next]
```

## Success Criteria

- Generate at least `10,000` transitions.
- Train an MLP transition model.
- Achieve low one-step MSE.
- Produce rollout plots comparing true vs predicted trajectories.
- Write `experiments/world-models/reports/stage1.md`.

---

### Task 1: Create experiment package skeleton

**Objective:** Create the world-model experiment directory and Python package.

**Files:**

- Create: `experiments/world-models/README.md`
- Create: `experiments/world-models/pyproject.toml`
- Create: `experiments/world-models/src/world_models/__init__.py`
- Create: `experiments/world-models/src/world_models/device.py`
- Create: `experiments/world-models/runs/.gitkeep`

**Step 1: Create `pyproject.toml`**

```toml
[project]
name = "ziyone-world-models"
version = "0.1.0"
description = "Small world model experiments for Apple M4 Pro"
requires-python = ">=3.11"
dependencies = [
  "torch",
  "numpy",
  "matplotlib",
  "pyyaml",
  "pytest",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

**Step 2: Add device helper**

```python
# experiments/world-models/src/world_models/device.py
from __future__ import annotations

import torch


def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")
```

**Step 3: Verify environment**

Run:

```bash
cd experiments/world-models
uv sync
uv run python -c "from world_models.device import get_device; print(get_device())"
```

Expected:

```text
mps
```

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: add experiment skeleton"
```

---

### Task 2: Implement synthetic state rollout dataset

**Objective:** Generate deterministic bouncing-ball transitions.

**Files:**

- Create: `experiments/world-models/src/world_models/datasets/state_rollout.py`
- Create: `experiments/world-models/tests/test_bouncing_ball.py`

**Step 1: Write test**

```python
from world_models.datasets.state_rollout import step_state, generate_transitions


def test_step_state_shape():
    next_state = step_state([0.5, 0.5, 0.1, 0.0], [0.0, -0.01], dt=1.0)
    assert len(next_state) == 4


def test_generate_transitions_shape():
    x, a, y = generate_transitions(n=128, seed=0)
    assert x.shape == (128, 4)
    assert a.shape == (128, 2)
    assert y.shape == (128, 4)
```

**Step 2: Implement minimal dataset**

```python
import numpy as np


def step_state(state, action, dt=1.0):
    x, y, vx, vy = map(float, state)
    ax, ay = map(float, action)
    vx = vx + ax * dt
    vy = vy + ay * dt
    x = x + vx * dt
    y = y + vy * dt

    if x < 0.0:
        x = -x
        vx = abs(vx)
    if x > 1.0:
        x = 2.0 - x
        vx = -abs(vx)
    if y < 0.0:
        y = -y
        vy = abs(vy)
    if y > 1.0:
        y = 2.0 - y
        vy = -abs(vy)

    return np.array([x, y, vx, vy], dtype=np.float32)


def generate_transitions(n=10_000, seed=0):
    rng = np.random.default_rng(seed)
    states = rng.uniform([0.1, 0.1, -0.03, -0.03], [0.9, 0.9, 0.03, 0.03], size=(n, 4)).astype(np.float32)
    actions = rng.uniform(-0.005, 0.005, size=(n, 2)).astype(np.float32)
    next_states = np.stack([step_state(s, a) for s, a in zip(states, actions)]).astype(np.float32)
    return states, actions, next_states
```

**Step 3: Verify**

Run:

```bash
cd experiments/world-models
uv run pytest tests/test_bouncing_ball.py -v
```

Expected: `2 passed`.

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: add state rollout dataset"
```

---

### Task 3: Train MLP transition model

**Objective:** Train the first world model: numeric state + action to next state.

**Files:**

- Create: `experiments/world-models/src/world_models/models/state_mlp.py`
- Create: `experiments/world-models/src/world_models/training/train_state_model.py`
- Create: `experiments/world-models/tests/test_state_model.py`
- Create: `experiments/world-models/configs/stage1_state.yaml`

**Model:**

```python
import torch
from torch import nn


class StateTransitionMLP(nn.Module):
    def __init__(self, state_dim=4, action_dim=2, hidden_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, state_dim),
        )

    def forward(self, state, action):
        return self.net(torch.cat([state, action], dim=-1))
```

**Training target:**

```text
loss = MSE(predicted_next_state, true_next_state)
```

**Config:**

```yaml
seed: 0
num_transitions: 50000
batch_size: 512
epochs: 50
learning_rate: 0.001
hidden_dim: 128
```

**Verification:**

Run:

```bash
cd experiments/world-models
uv run python -m world_models.training.train_state_model --config configs/stage1_state.yaml
```

Expected:

```text
final_train_mse < 1e-4
```

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: train state transition model"
```

---

### Task 4: Add rollout evaluation and report

**Objective:** Evaluate multi-step prediction drift.

**Files:**

- Create: `experiments/world-models/src/world_models/evaluation/rollout.py`
- Create: `experiments/world-models/src/world_models/evaluation/plots.py`
- Create: `experiments/world-models/reports/stage1.md`

**Evaluation:**

- Start from one initial state.
- Roll out true dynamics for `100` steps.
- Roll out model predictions for `100` steps.
- Plot true and predicted XY trajectory.

**Report template:**

```markdown
# Stage 1 Report — State World Model

## Setup

- Machine: Apple M4 Pro, 64 GB unified memory
- Backend: MPS or CPU
- Dataset: synthetic bouncing ball state transitions

## Results

- One-step MSE:
- 100-step rollout behavior:
- Failure cases:

## Lessons

- What the model learned:
- What it failed to learn:
- What changes for Stage 2:
```

**Verification:**

Run:

```bash
cd experiments/world-models
uv run python -m world_models.evaluation.rollout --checkpoint runs/stage1_state.pt
```

Expected:

```text
runs/stage1_rollout.png exists
```

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: add state rollout evaluation"
```

---

# Stage 2 — Small Image Latent World Model

## Learning Objective

Move from explicit numeric state to learned visual representation.

Architecture:

```text
image_t -> CNN encoder -> latent_t
latent_t + action_t -> dynamics model -> latent_{t+1}
latent_{t+1} -> decoder -> reconstructed image_{t+1}
```

This stage teaches representation learning, latent dynamics, and visual rollout.

## Dataset

Use the same bouncing-ball simulator, but render frames at `64×64`.

Input:

```text
image_t: 64×64 grayscale or RGB
optional action_t: [ax, ay]
```

Target:

```text
image_{t+1}
```

## Success Criteria

- Generate at least `50,000` image transitions.
- Train an autoencoder that reconstructs frames.
- Train latent dynamics that predicts next latent.
- Decode predicted latent to next frame.
- Produce side-by-side plots: current frame, true next frame, predicted next frame.
- Write `experiments/world-models/reports/stage2.md`.

---

### Task 5: Add image renderer for bouncing ball

**Objective:** Render numeric ball states into small images.

**Files:**

- Create: `experiments/world-models/src/world_models/datasets/bouncing_ball.py`
- Create: `experiments/world-models/tests/test_image_shapes.py`

**Test:**

```python
from world_models.datasets.bouncing_ball import render_ball, generate_image_transitions


def test_render_ball_shape():
    image = render_ball([0.5, 0.5, 0.01, 0.0], size=64)
    assert image.shape == (1, 64, 64)


def test_generate_image_transitions_shape():
    image, action, next_image = generate_image_transitions(n=32, size=64, seed=0)
    assert image.shape == (32, 1, 64, 64)
    assert action.shape == (32, 2)
    assert next_image.shape == (32, 1, 64, 64)
```

**Verification:**

```bash
cd experiments/world-models
uv run pytest tests/test_image_shapes.py -v
```

Expected: `2 passed`.

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: render bouncing ball images"
```

---

### Task 6: Train CNN autoencoder

**Objective:** Learn compact visual latent representations.

**Files:**

- Create: `experiments/world-models/src/world_models/models/cnn_autoencoder.py`
- Modify: `experiments/world-models/src/world_models/training/train_image_latent.py`
- Create: `experiments/world-models/configs/stage2_image_latent.yaml`

**Recommended config for Apple M4 Pro:**

```yaml
seed: 0
image_size: 64
num_transitions: 50000
batch_size: 128
latent_dim: 64
epochs_autoencoder: 30
learning_rate: 0.001
```

**Model shape contract:**

```text
encoder: [B, 1, 64, 64] -> [B, 64]
decoder: [B, 64] -> [B, 1, 64, 64]
```

**Verification:**

Run:

```bash
cd experiments/world-models
uv run python -m world_models.training.train_image_latent --config configs/stage2_image_latent.yaml --phase autoencoder
```

Expected:

```text
runs/stage2_autoencoder.pt exists
runs/stage2_recon_grid.png exists
```

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: train image autoencoder"
```

---

### Task 7: Train latent dynamics model

**Objective:** Predict the next latent vector from current latent and action.

**Files:**

- Create: `experiments/world-models/src/world_models/models/latent_dynamics.py`
- Modify: `experiments/world-models/src/world_models/training/train_image_latent.py`

**Architecture:**

```text
latent_t + action_t -> MLP/GRU -> predicted_latent_{t+1}
```

Start with MLP before GRU.

**Loss:**

```text
MSE(predicted_latent_next, encoder(next_image).detach())
```

**Verification:**

Run:

```bash
cd experiments/world-models
uv run python -m world_models.training.train_image_latent --config configs/stage2_image_latent.yaml --phase dynamics
```

Expected:

```text
runs/stage2_latent_dynamics.pt exists
```

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: train latent dynamics model"
```

---

### Task 8: Add image rollout evaluation and report

**Objective:** Visualize predicted future frames.

**Files:**

- Modify: `experiments/world-models/src/world_models/evaluation/rollout.py`
- Modify: `experiments/world-models/src/world_models/evaluation/plots.py`
- Create: `experiments/world-models/reports/stage2.md`

**Evaluation:**

- Given initial image and actions, predict `10` future frames.
- Decode predicted latents to images.
- Save a grid with true vs predicted frames.

**Report template:**

```markdown
# Stage 2 Report — Image Latent World Model

## Setup

- Image size:
- Latent dimension:
- Backend:
- Training time:

## Results

- Reconstruction quality:
- One-step latent MSE:
- Multi-step rollout drift:

## Lessons

- What the model learned visually:
- Where predictions fail:
- What Stage 3 changes by removing pixel reconstruction pressure:
```

**Verification:**

```bash
cd experiments/world-models
uv run python -m world_models.evaluation.rollout --mode image --checkpoint runs/stage2_latent_dynamics.pt
```

Expected:

```text
runs/stage2_image_rollout.png exists
```

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: evaluate image latent rollouts"
```

---

# Stage 3 — Mini JEPA-Style Latent Prediction

## Learning Objective

Build the smallest version of the LeCun / JEPA idea:

```text
Do not reconstruct pixels.
Predict target embeddings from context embeddings.
```

This stage should clarify the conceptual difference between:

```text
generative image prediction: predict pixels
JEPA-style prediction: predict representations
```

## Minimum JEPA Setup

Input sequence:

```text
frame_t, frame_{t+1}, frame_{t+2}
```

Context:

```text
frame_t, optional action_t
```

Target:

```text
frame_{t+1} or frame_{t+2}
```

Architecture:

```text
context_frame -> context_encoder -> context_embedding
 target_frame -> target_encoder  -> target_embedding
context_embedding + action -> predictor -> predicted_target_embedding
loss = MSE(predicted_target_embedding, stopgrad(target_embedding))
```

Anti-collapse minimum options:

1. Start with frozen or EMA target encoder.
2. Add variance regularization if collapse appears.
3. Track embedding standard deviation during training.

## Success Criteria

- Train without representation collapse.
- Show decreasing prediction loss.
- Track embedding variance over time.
- Use learned embeddings for a downstream probe: predict ball position from embedding.
- Write `experiments/world-models/reports/stage3.md`.

---

### Task 9: Add Mini-JEPA model shape tests

**Objective:** Define and verify the model interfaces before training.

**Files:**

- Create: `experiments/world-models/src/world_models/models/mini_jepa.py`
- Create: `experiments/world-models/tests/test_jepa_shapes.py`
- Create: `experiments/world-models/configs/stage3_mini_jepa.yaml`

**Test:**

```python
import torch
from world_models.models.mini_jepa import MiniJEPA


def test_mini_jepa_shapes():
    model = MiniJEPA(image_channels=1, embedding_dim=128, action_dim=2)
    context = torch.randn(4, 1, 64, 64)
    target = torch.randn(4, 1, 64, 64)
    action = torch.randn(4, 2)
    pred, target_emb = model(context, target, action)
    assert pred.shape == (4, 128)
    assert target_emb.shape == (4, 128)
```

**Recommended config for Apple M4 Pro:**

```yaml
seed: 0
image_size: 64
num_sequences: 50000
batch_size: 128
embedding_dim: 128
epochs: 50
learning_rate: 0.0005
ema_decay: 0.99
variance_floor: 0.05
```

**Verification:**

```bash
cd experiments/world-models
uv run pytest tests/test_jepa_shapes.py -v
```

Expected: `1 passed`.

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: add mini jepa model contract"
```

---

### Task 10: Train Mini-JEPA with collapse monitoring

**Objective:** Train context-to-target embedding prediction and detect collapse.

**Files:**

- Create: `experiments/world-models/src/world_models/training/train_mini_jepa.py`
- Modify: `experiments/world-models/src/world_models/models/mini_jepa.py`

**Training loop metrics:**

```text
prediction_loss
embedding_std_mean
embedding_std_min
learning_rate
```

**Collapse warning rule:**

```text
if embedding_std_mean < 0.05 for 3 epochs:
    warn: representation collapse likely
```

**Loss:**

```text
prediction_loss = MSE(predicted_target_embedding, target_embedding.detach())
variance_loss = mean(relu(variance_floor - std(target_embedding)))
total_loss = prediction_loss + 0.1 * variance_loss
```

**Verification:**

Run:

```bash
cd experiments/world-models
uv run python -m world_models.training.train_mini_jepa --config configs/stage3_mini_jepa.yaml
```

Expected:

```text
runs/stage3_mini_jepa.pt exists
embedding_std_mean stays above 0.05
prediction_loss decreases across training
```

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: train mini jepa"
```

---

### Task 11: Add downstream probe for learned embeddings

**Objective:** Test whether embeddings contain physical state information.

**Files:**

- Create: `experiments/world-models/src/world_models/evaluation/probe_embeddings.py`
- Create: `experiments/world-models/reports/stage3.md`

**Probe:**

Freeze context encoder and train a small linear model:

```text
embedding -> [x, y]
```

If the probe predicts ball position well, the representation contains useful physical information.

**Metrics:**

```text
probe_train_mse
probe_test_mse
scatter plot: true x/y vs predicted x/y
```

**Verification:**

```bash
cd experiments/world-models
uv run python -m world_models.evaluation.probe_embeddings --checkpoint runs/stage3_mini_jepa.pt
```

Expected:

```text
runs/stage3_probe.png exists
probe_test_mse is meaningfully better than random baseline
```

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: probe mini jepa embeddings"
```

---

### Task 12: Compare Stage 2 and Stage 3

**Objective:** Write the final comparison explaining what changed conceptually.

**Files:**

- Create: `experiments/world-models/reports/comparison.md`
- Modify: `experiments/world-models/README.md`

**Comparison questions:**

```markdown
# World Model Stages Comparison

## Stage 1: Explicit State Dynamics

- What was easy?
- What was unrealistic?

## Stage 2: Image Latent Dynamics

- What did reconstruction help with?
- What did reconstruction waste capacity on?

## Stage 3: Mini JEPA

- Did latent prediction train stably?
- Did embeddings avoid collapse?
- Did embeddings preserve position / velocity information?

## Key Takeaway

Explain the difference between:

- predicting pixels
- predicting latent representations
- planning in latent space
```

**Verification:**

Run:

```bash
cd experiments/world-models
uv run pytest -v
```

Expected: all tests pass.

Commit:

```bash
git add experiments/world-models
git commit -m "world-models: compare learning stages"
```

---

# Recommended Timeline

## Week 1 — Stage 1

Goal: understand world-model basics.

```text
Day 1: package skeleton + dataset
Day 2: MLP transition model
Day 3: rollout evaluation
Day 4: write Stage 1 report
```

## Week 2 — Stage 2

Goal: learn visual latent dynamics.

```text
Day 1: image renderer
Day 2: CNN autoencoder
Day 3: latent dynamics
Day 4: image rollout visualization
Day 5: write Stage 2 report
```

## Week 3 — Stage 3

Goal: understand JEPA-style latent prediction.

```text
Day 1: Mini-JEPA model contract
Day 2: training loop + collapse metrics
Day 3: tune anti-collapse settings
Day 4: downstream probe
Day 5: write Stage 3 report and comparison
```

Total expected time:

```text
Focused implementation: 2–3 weeks
Casual learning pace: 4–6 weeks
```

---

# Validation Checklist

Before considering the roadmap complete:

- [ ] Stage 1 trains on M4 Pro and produces a trajectory plot.
- [ ] Stage 1 report explains transition modeling and rollout drift.
- [ ] Stage 2 trains on MPS and produces reconstruction + rollout images.
- [ ] Stage 2 report explains latent dynamics and pixel reconstruction limitations.
- [ ] Stage 3 trains without collapse.
- [ ] Stage 3 logs embedding variance.
- [ ] Stage 3 probe shows embeddings encode ball position.
- [ ] Final comparison explains LeCun / JEPA motivation in plain language.

---

# Stretch Goals After Stage 3

Only attempt these after the three core stages are complete:

1. Replace bouncing ball with `gymnasium` CartPole rendered images.
2. Add sequence model dynamics with GRU or small Transformer.
3. Try 96×96 or 128×128 images.
4. Add action-conditioned planning with random shooting / MPC.
5. Compare pixel prediction vs latent prediction on long rollouts.
6. Read and summarize:
   - `A Path Towards Autonomous Machine Intelligence`
   - `I-JEPA`
   - `V-JEPA`
   - `V-JEPA 2`
   - `LeWorldModel`

---

# Practical Recommendation

For this machine, the best first implementation should use:

```text
image_size: 64
batch_size: 128
latent_dim: 64 or 128
embedding_dim: 128
num_transitions: 50,000
```

If MPS memory or speed becomes a problem:

```text
batch_size: 128 -> 64 -> 32
image_size: 64 stays fixed
embedding_dim: 128 -> 64
num_transitions: 50,000 -> 10,000 for debugging
```

Do not start with 224×224 or a ViT. The goal is to understand the world-model learning loop first, not to reproduce a large paper immediately.
