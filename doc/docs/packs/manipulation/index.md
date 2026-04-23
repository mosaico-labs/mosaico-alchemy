---
title: Manipulation Pack
---

The **Manipulation Pack** is a curated collection of heterogeneous open-source robotic manipulation datasets, each individually studied, analyzed, and mapped into Mosaico's unified semantic ontology. Every dataset was manually inspected to identify its internal topics and data streams; custom ontologies were written specifically to represent the physical semantics of each source format, from HDF5 to Parquet, from TensorFlow Records to ROS bags.

The result is a single, ready-to-use ingestion suite where a [`RobotJoint`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.RobotJoint) topic originating from a ROS bag looks and behaves exactly like a [`RobotJoint`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.RobotJoint) topic coming from a DeepMind TFRecord. This is the core value proposition: proving that Mosaico acts as the universal standard for semantic sensor data description across deeply fragmented ecosystems.

<!-- ### Installation

Install the manipulation pack via pip:

```bash
pip install mosaico-alchemy[manipulation]
```

*Note: Requires Python 3.10 or higher.* -->

### Basic Usage

From your terminal, use the `mosaico_alchemy manipulation` command followed by your dataset directories:

```bash
mosaico_alchemy manipulation --datasets /path/to/dataset
```

### Configuration Options

The CLI supports the following flags to control the execution environment:

| Option | Default | Description |
| :--- | :--- | :--- |
| `--datasets` | Required | One or more space-separated dataset roots to ingest. |
| `--host` | `localhost` | The hostname of your Mosaico Server. |
| `--port` | `6726` | The Flight port of your Mosaico Server. |
| `--log-level` | `INFO` | Set verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `--write-mode` | `sync` | Topic execution mode for file-backed data (`sync` or `async`). |

### Supported Datasets

We provide built-in support for multiple open-source formats. We recommend exploring them in the following order to understand the offered capabilities:

#### [Reassemble](https://researchdata.tuwien.ac.at/records/0ewrv-8cb44)

4,551 contact-rich assembly and disassembly demonstrations across 17 objects, with multimodal sensing from event cameras, force-torque sensors, microphones and multi-view RGB cameras.

!!! info "Execution Backend: File (HDF5)"

??? success "Topics Ingested into Mosaico"
    | Topic | Ontology Type |
    | :--- | :--- |
    | `capture_node-camera-image` | [`CompressedImage`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.CompressedImage) |
    | `events` | `EventCamera` |
    | `hama1` | [`CompressedImage`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.CompressedImage) |
    | `hama1_audio` | `AudioDataStamped` |
    | `hama2` | [`CompressedImage`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.CompressedImage) |
    | `hama2_audio` | `AudioDataStamped` |
    | `hand` | [`CompressedImage`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.CompressedImage) |
    | `hand_audio` | `AudioDataStamped` |
    | `robot_state/joint_state` | [`RobotJoint`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.RobotJoint) |
    | `robot_state/pose` | [`Pose`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Pose) |
    | `robot_state/velocity` | [`Velocity`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.kinematics.Velocity) |
    | `robot_state/compensated_base_force_torque` | [`ForceTorque`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.dynamics.ForceTorque) |
    | `robot_state/measured_force_torque` | [`ForceTorque`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.dynamics.ForceTorque) |
    | `robot_state/end_effector` | `EndEffector` |

??? quote "Citation"
    Sliwowski, D. J., Jadav, S., Stanovcic, S., Orbik, J., Heidersberger, J., & Lee, D. (2025). REASSEMBLE: A Multimodal Dataset for Contact-rich Robotic Assembly and Disassembly (1.0.0) [Data set]. TU Wien. https://doi.org/10.48436/0ewrv-8cb44

#### [RT-1 (Fractal)](https://www.tensorflow.org/datasets/catalog/fractal20220817_data)

87,212 pick-and-place episodes across 17 objects in Google micro kitchen environments, with RGB observations, natural language instructions, 512D task embeddings and full end-effector action space.

!!! info "Execution Backend: File (TFDS)"

??? success "Topics Ingested into Mosaico"
    | Topic | Ontology Type |
    | :--- | :--- |
    | `step/observation/image` | [`CompressedImage`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.CompressedImage) |
    | `step/observation/base_pose_tool_reached` | [`Pose`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Pose) |
    | `step/observation/orientation_start` | [`Quaternion`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Quaternion) |
    | `step/observation/src_rotation` | [`Quaternion`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Quaternion) |
    | `step/observation/natural_language_instruction` | [`String`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.String) |
    | `step/observation/natural_language_embedding` | `TextEmbedding` |
    | `step/observation/gripper_closed` | [`Floating32`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Floating32) |
    | `step/observation/gripper_closedness_commanded` | [`Floating32`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Floating32) |
    | `step/observation/height_to_bottom` | [`Floating32`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Floating32) |
    | `step/observation/rotation_delta_to_go` | [`Vector3d`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Vector3d) |
    | `step/observation/vector_to_go` | [`Vector3d`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Vector3d) |
    | `step/observation/orientation_box` | `Vector3dBounds` |
    | `step/observation/robot_orientation_positions_box` | `Vector3dFrame` |
    | `step/observation/workspace_bounds` | `WorkspaceBounds` |
    | `step/action/world_vector` | [`Vector3d`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Vector3d) |
    | `step/action/rotation_delta` | [`Vector3d`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Vector3d) |
    | `step/action/base_displacement_vector` | [`Vector3d`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Vector2d) |
    | `step/action/base_displacement_vertical_rotation` |  [`Floating32`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Floating32) |
    | `step/action/gripper_closedness_action` |  [`Floating32`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Floating32) |
    | `step/action/terminate_episode` | `TerminateEpisode` |
    | `step/reward` |  [`Floating32`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Floating32) |
    | `step/is_first` |  [`Boolean`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Boolean) |
    | `step/is_last` |  [`Boolean`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Boolean) |
    | `step/is_terminal` |  [`Boolean`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Boolean) |

??? quote "Citation"
    ```bibtex
    @article{brohan2022rt,
      title={Rt-1: Robotics transformer for real-world control at scale},
      author={Brohan, Anthony and Brown, Noah and Carbajal, Justice and Chebotar, Yevgen and Dabis, Joseph and Finn, Chelsea and Gopalakrishnan, Keerthana and Hausman, Karol and Herzog, Alex and Hsu, Jasmine and others},
      journal={arXiv preprint arXiv:2212.06817},
      year={2022}
    }


#### [LeRobot DROID](https://huggingface.co/datasets/lerobot/droid_1.0.1)

95,658 manipulation episodes collected at 13 research institutions, with wrist and dual exterior stereo cameras, joint and Cartesian state, end-effector position and embedded camera extrinsics.

!!! info "Execution Backend: File (Parquet)"

??? success "Topics Ingested into Mosaico"
    | Topic | Ontology Type |
    | :--- | :--- |
    | `/observation/images/wrist_left` | [`CompressedImage`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.CompressedImage) |
    | `/observation/images/exterior_1_left` | [`CompressedImage`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.CompressedImage) |
    | `/observation/images/exterior_2_left` | [`CompressedImage`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.CompressedImage) |
    | `/observation/state/joint_position` | [`RobotJoint`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.RobotJoint) |
    | `/observation/state/cartesian_position` | [`Pose`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Pose) |
    | `/observation/state/gripper_position` | `EndEffector` |
    | `/action/joint_position` | [`RobotJoint`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.RobotJoint) |
    | `/action/cartesian_position` | [`Pose`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Pose) |
    | `/action/cartesian_velocity` | [`Velocity`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.kinematics.Velocity) |
    | `/action/gripper_position` | `EndEffector` |
    | `/camera_extrinsics/wrist_left` | [`Pose`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Pose) |
    | `/camera_extrinsics/exterior_1_left` | [`Pose`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Pose) |
    | `/camera_extrinsics/exterior_2_left` | [`Pose`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Pose) |
    | `/step/reward` | [`Floating64`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Floating64) |
    | `/step/discount` | [`Floating64`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Floating64) |
    | `/step/task_index` | [`Integer64`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Integer64) |
    | `/step/frame_index` | [`Integer64`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Integer64) |
    | `/step/is_first` |  [`Boolean`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Boolean) |
    | `/step/is_last` |  [`Boolean`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Boolean) |
    | `/step/is_terminal` |  [`Boolean`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.Boolean) |

??? quote "Citation"
    ```bibtex
    @article{khazatsky2024droid,
        title   = {DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset},
        author  = {Alexander Khazatsky and Karl Pertsch and Suraj Nair and Ashwin Balakrishna and Sudeep Dasari and Siddharth Karamcheti and Soroush Nasiriany and Mohan Kumar Srirama and Lawrence Yunliang Chen and Kirsty Ellis and Peter David Fagan and Joey Hejna and Masha Itkina and Marion Lepert and Yecheng Jason Ma and Patrick Tree Miller and Jimmy Wu and Suneel Belkhale and Shivin Dass and Huy Ha and Arhan Jain and Abraham Lee and Youngwoon Lee and Marius Memmel and Sungjae Park and Ilija Radosavovic and Kaiyuan Wang and Albert Zhan and Kevin Black and Cheng Chi and Kyle Beltran Hatch and Shan Lin and Jingpei Lu and Jean Mercat and Abdul Rehman and Pannag R Sanketi and Archit Sharma and Cody Simpson and Quan Vuong and Homer Rich Walke and Blake Wulfe and Ted Xiao and Jonathan Heewon Yang and Arefeh Yavary and Tony Z. Zhao and Christopher Agia and Rohan Baijal and Mateo Guaman Castro and Daphne Chen and Qiuyu Chen and Trinity Chung and Jaimyn Drake and Ethan Paul Foster and Jensen Gao and Vitor Guizilini and David Antonio Herrera and Minho Heo and Kyle Hsu and Jiaheng Hu and Muhammad Zubair Irshad and Donovon Jackson and Charlotte Le and Yunshuang Li and Kevin Lin and Roy Lin and Zehan Ma and Abhiram Maddukuri and Suvir Mirchandani and Daniel Morton and Tony Nguyen and Abigail O'Neill and Rosario Scalise and Derick Seale and Victor Son and Stephen Tian and Emi Tran and Andrew E. Wang and Yilin Wu and Annie Xie and Jingyun Yang and Patrick Yin and Yunchu Zhang and Osbert Bastani and Glen Berseth and Jeannette Bohg and Ken Goldberg and Abhinav Gupta and Abhishek Gupta and Dinesh Jayaraman and Joseph J Lim and Jitendra Malik and Roberto Martín-Martín and Subramanian Ramamoorthy and Dorsa Sadigh and Shuran Song and Jiajun Wu and Michael C. Yip and Yuke Zhu and Thomas Kollar and Sergey Levine and Chelsea Finn},
        year    = {2024},
    }
    ```

#### [Multimodal Manipulation Learning](https://zenodo.org/records/6372438)

300 ROS bag recordings of a Kuka IIWA robot with Allegro hand, combining Tekscan tactile pressure, microphone audio, torque commands and joint states across 5 material classes.

!!! info "Execution Backend: ROS `.bag`"

??? success "Topics Ingested into Mosaico"
    | Topic | Ontology Type |
    | :--- | :--- |
    | `/allegro_hand_right/joint_states` | [`RobotJoint`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.RobotJoint) |
    | `/iiwa/joint_states` | [`RobotJoint`](https://docs.mosaico.dev/SDK/API_reference/models/sensors/#mosaicolabs.models.sensors.RobotJoint) |
    | `/iiwa/eePose` | [`Pose`](https://docs.mosaico.dev/SDK/API_reference/models/geometry/#mosaicolabs.models.data.geometry.Pose) |
    | `/iiwa/TorqueController/command` | `JointTorqueCommand` |
    | `/tekscan/frame` | `TekscanSensor` |
    | `/audio/audio` | `AudioDataStamped` |
    | `/audio/audio_info` | `AudioInfo` |
    | `/trialInfo` | [`String`](https://docs.mosaico.dev/SDK/API_reference/models/data_types/#mosaicolabs.models.data.base_types.String) |

??? quote "Citation"
    Prabhakar, A., Billard, A., & Reber, D. (2021). Multimodal Sensory Learning for Object Manipulation (v1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.6372438

### Ready to start?

If your robotic data is saved in a proprietary format and isn't supported out-of-the-box, the module is fully extensible. 
We recommend jumping directly to the **[Integrating a Dataset](./extending.md)** guide to build your own plugin, custom ontologies and adapters.