# The code of lesson 58, shared by the step script and the page's checkpoint.
EDITORCONFIG = '''root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = tab

[*.{cs,csproj,sln}]
indent_size = 4

[*.cs]
csharp_style_namespace_declarations = file_scoped:warning
dotnet_sort_system_directives_first = true
csharp_new_line_before_open_brace = all
dotnet_style_qualification_for_field = false:suggestion
csharp_style_var_for_built_in_types = true:suggestion
csharp_style_var_when_type_is_apparent = true:suggestion
'''

CSPROJ = '''<Project Sdk="Godot.NET.Sdk/4.8.0-beta.1">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <EnableDynamicLoading>true</EnableDynamicLoading>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
'''
