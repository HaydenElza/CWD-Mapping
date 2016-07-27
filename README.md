# Coarse Woody Debris Mapping

This is a tool for mapping coarse woody debris. In the field points are recorded at the start and end of logs and when applicable, at nodes of forks.

---

### Labeling Method

Labels, i.e. the *ID* field, consist of two parts. A four character TreeID, then a variable length NodeID.

Example:	ID=06931		Tree #693, Node 1

Node ID schema:

1. 0 at the big end of the log, 1 at the small end
2. At each fork start a new level, i.e., a new character place. The first character is the node it connects to, the second is the fork number

Example: if there are three forks from one node, there will be NodeIDs of 10, 11, 12. The first character 1 refers to the parent node. The second characters 0, 1, and 2 refer to the first, second, and third forks coming from the parent node 1.

![](/screenshots/label_examples.png?raw=true)

Example ID: <span style="color: red;">0693112</span>

If you make a mistake or have to reshoot something after already saving/labeling it, simply label the correct/reshot point as underscore then reshoot number.

Example: 0693112_1 or 0963112_2 for reshoot 1 and 2 respectively

---

### How to Use Tool

1. Open ArcCatelog or ArcMap
2. Add the *CWD_mapping* toolbox
3. Open CWD Mapping script and select point dataset.
![](/screenshots/tool_window.png?raw=true)


Input | Output
:---: | :----:
![](/screenshots/points.png?raw=true) | ![](/screenshots/lines.png?raw=true)

---

### Test Data

Test data are included to familiarize yourself with the tool.

Descriptions:

1. Normal
2. Contains re-shoots
3. Contains multiple re-shoots per log
4. Contains duplicate IDs (will return error)
5. Contains ID with invalid characters (will return error)