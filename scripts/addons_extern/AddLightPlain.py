emission = node_tree.nodes.new('ShaderNodeEmission')
lightpath = node_tree.nodes.new('ShaderNodeLightPath')


node_tree.links.new(out_node.inputs[0], emission.outputs[0])
node_tree.links.new(emission.inputs[0], tex_image.outputs[0])
node_tree.links.new(emission.inputs[1], lightpath.outputs[0])
