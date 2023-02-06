import unreal

class Material:
    def __init__(self, name, create = False):
        self.AR = unreal.AssetRegistryHelpers.get_asset_registry()
        self.AT = unreal.AssetToolsHelpers.get_asset_tools()
        self.MEL = unreal.MaterialEditingLibrary
        if not create:
            for x in self.AR.get_all_assets():
                if x.asset_name == name and x.package_path == "/Game" and x.asset_class_path.asset_name == "Material":
                    self.material = unreal.AssetRegistryHelpers.get_asset(x)
                    return
        self.material = self.AT.create_asset(name, "/Game", unreal.Material, unreal.MaterialFactoryNew())
        self.save()

    def save(self):
        unreal.EditorAssetLibrary.save_asset(self.material.get_path_name())

    def dump(self, file_name):
        with open(file_name, 'w') as f:
            editor_properties = {}
            tmp_nodes = []
            for p in unreal.MaterialProperty:
                n = self.MEL.get_material_property_input_node(self.material, p)
                if n != None:
                    tmp_nodes.append(n)
            nodes = []
            while len(tmp_nodes) != 0:
                new_tmp_nodes = []
                for n in tmp_nodes:
                    if n != None and not n in nodes:
                        nodes.append(n)
                        for i in self.MEL.get_inputs_for_material_expression(self.material, n):
                            new_tmp_nodes.append(i)
                tmp_nodes = new_tmp_nodes
            f.write("import unreal\n")
            f.write("import mm\n")
            f.write("from importlib import reload\n")
            f.write("reload(mm)\n")

            f.write("mat = mm.Material('my_material_name', True)\n")
            f.write("mat.clear()\n")
            node_dict = {}
            for n in nodes:
                name = n.get_name()[18:]
                node_dict[n] = name
                f.write(name+" = mat.add_node('"+n.__class__.__name__[18:]+"', "+str(n.material_expression_editor_x)+", "+str(n.material_expression_editor_y)+")\n")
                for p in [ "material_function", "code", "output_type", "additional_defines", "additional_outputs", "inputs" ]:
                    try:
                        pv = n.get_editor_property(p)
                    except:
                        continue
                    if isinstance(pv, unreal.Object):
                        pv = "mm.find_object_by_fname('"+str(pv.get_fname())+"')"
                    elif isinstance(pv, unreal.EnumBase):
                        pv = str(pv)
                        pv = "unreal."+pv[pv.find('<')+1:pv.find(':')]
                    elif pv is list:
                        l = []
                        for e in pv:
                            l.append(str(e))
                        pv = "["+", ".join(l)+"]"
                    else:
                        print("# "+p+" is a "+str(type(pv)))
                        pv = str(pv)
                    f.write(name+".set_editor_property('"+p+"', "+pv+")\n")
            for p in unreal.MaterialProperty:
                n = self.MEL.get_material_property_input_node(self.material, p)
                if n != None:
                    o = self.MEL.get_material_property_input_node_output_name(self.material, p)
                    property_name = str(p)
                    property_name = property_name[property_name.find('<')+1:property_name.find(':')]
                    f.write("mat.connect_property("+node_dict[n]+", '"+o+"', unreal."+property_name+")\n")
            for n in nodes:
                for i in self.MEL.get_inputs_for_material_expression(self.material, n):
                    if i != None:
                        ip = self.MEL.get_input_node_output_name_for_material_expression(n, i)
                        op = ""
                        f.write("mat.connect_nodes("+node_dict[i]+", '"+ip+"', "+node_dict[n]+", '"+op+"')\n")
            f.write("mat.save()\n")
            f.close()

    def clear(self):
        self.MEL.delete_all_material_expressions(self.material)

    def add_node(self, type, x=0, y=0):
        return self.MEL.create_material_expression(self.material, getattr(unreal, "MaterialExpression"+type), x, y)

    def connect_property(self, source, source_output, property):
        return self.MEL.connect_material_property(source, source_output, property)

    def connect_nodes(self, source, source_output, dest, dest_input):
        return self.MEL.connect_material_expressions(source, source_output, dest, dest_input)

def find_object_by_fname(n):
    it = unreal.ObjectIterator()
    for x in it:
        if x.get_fname() == n:
            return x

def read_text_file(path):
    with open(path, 'r') as f:
        return f.read()
    return ''

def read_texture_file(path):
    return None

#mat = Material("material_dynamic")
#mat.dump("D:\\Dev\\Godot\\material-maker-bugfix\\material_maker\\misc\\export\\test.py")
