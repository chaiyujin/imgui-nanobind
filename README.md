# imgui-nanobind

Overwrite

```cpp
.def("contains_point", [](ImRect const & r, ImVec2 const & p) -> bool { return r.Contains(p); })
.def("contains_rect",  [](ImRect const & r, ImRect const & b) -> bool { return r.Contains(b); })
.def("overlaps",       [](ImRect const & r, ImRect const & b) -> bool { return r.Overlaps(b); })
.def("add_point",      [](ImRect & r, ImVec2 const & p) { r.Add(p); })
.def("add_rect",       [](ImRect & r, ImRect const & b) { r.Add(b); })
.def("expand_both",    [](ImRect & r, float b) { r.Expand(b); })
.def("expand_each",    [](ImRect & r, ImVec2 const & b) { r.Expand(b); })
```
