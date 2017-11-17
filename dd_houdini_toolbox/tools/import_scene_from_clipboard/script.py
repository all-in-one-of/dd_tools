import hou

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui


class import_scene_from_clipboard():
    # ('SettingsCameraDof', 'aperture'),
    metric_parms = (('SettingsCameraDof', 'focal_dist'), ('TexDirt', 'radius'),
                    ('LightIES', 'shadowBias'), ('LightDome', 'shadowBias'), ('LightDome', 'dome_rayDistance'),
                    ('LightRectangle', 'u_size'), ('LightRectangle', 'v_size'), ('LightRectangle', 'shadowBias'),
                    ('LightSphere', 'radius'), ('LightSphere', 'shadowBias'),
                    ('LightMesh', 'shadowBias'),
                    ('SunLight', 'shadowBias'), ('SunLight', 'photon_radius'),
                    ('LightAmbientMax', 'gi_min_distance'),
                    ('LightIESMax', 'shadowBias'), ('LightIESMax', 'ies_light_width'),
                    ('LightIESMax', 'ies_light_length'), ('LightIESMax', 'ies_light_height'),
                    ('LightIESMax', 'ies_light_diameter'),
                    ('LightSpotMax', 'shadowBias'), ('LightSpotMax', 'near_attenuation_start'),
                    ('LightSpotMax', 'near_attenuation_end'),
                    ('LightSpotMax', 'far_attenuation_start'), ('LightSpotMax', 'far_attenuation_end'),

                    ('LightDirectMax', 'shadowBias'), ('LightDirectMax', 'near_attenuation_start'),
                    ('LightDirectMax', 'near_attenuation_end'),
                    ('LightDirectMax', 'far_attenuation_start'), ('LightDirectMax', 'far_attenuation_end'),

                    ('LightOmniMax', 'shadowBias'), ('LightOmniMax', 'near_attenuation_start'),
                    ('LightOmniMax', 'near_attenuation_end'),
                    ('LightOmniMax', 'far_attenuation_start'), ('LightOmniMax', 'far_attenuation_end'),

                    ('RenderChannelZDepth', 'depth_black'), ('Mtl2Sided', 'translucency_tex_mult'),
                    ('TexFalloff', 'dist_near'), ('TexFalloff', 'dist_far'),
                    ('RenderChannelZDepth', 'depth_white'),
                    ('TexEdges', 'world_width'))  # parameters that need to be scaled

    deg_to_rad_parms = (('LightSpotMax', 'fallsize'), ('LightSpotMax', 'hotspot'))

    # ('SettingsColorMapping', 'exposure'),
    black_listed_parms = (('TexFalloff', 'use_blend_input'), ('RenderChannelMultiMatte', 'enableDeepOutput'),
                          ('SunLight', 'blend_angle'), ('SunLight', 'horizon_offset'), ('SunLight', 'target_transform'),
                          ('LightAmbientMax', 'mode'), ('LightAmbientMax', 'gi_min_distance'),
                          ('LightAmbientMax', 'color'),
                          ('LightAmbientMax', 'compensate_exposure'),
                          ('LightSpotMax', 'decay_type'), ('LightSpotMax', 'decay_start'),
                          ('LightSpotMax', 'near_attenuation'),
                          ('LightSpotMax', 'near_attenuation_start'), ('LightSpotMax', 'near_attenuation_end'),
                          ('LightSpotMax', 'far_attenuation'),
                          ('LightSpotMax', 'far_attenuation_start'), ('LightSpotMax', 'far_attenuation_end'),
                          ('LightSpotMax', 'fallsize'), ('LightSpotMax', 'hotspot'), ('LightSpotMax', 'shape_type'),
                          ('LightSpotMax', 'rect_aspect'),
                          ('LightSpotMax', 'overshoot'),
                          ('LightDirectMax', 'decay_type'), ('LightDirectMax', 'decay_start'),
                          ('LightDirectMax', 'near_attenuation'),
                          ('LightDirectMax', 'near_attenuation_start'), ('LightDirectMax', 'near_attenuation_end'),
                          ('LightDirectMax', 'far_attenuation'),
                          ('LightDirectMax', 'far_attenuation_start'), ('LightDirectMax', 'far_attenuation_end'),
                          ('LightDirectMax', 'fallsize'), ('LightDirectMax', 'hotspot'),
                          ('LightDirectMax', 'shape_type'), ('LightDirectMax', 'rect_aspect'),
                          ('LightDirectMax', 'overshoot'),
                          ('LightOmniMax', 'decay_type'), ('LightOmniMax', 'decay_start'),
                          ('LightOmniMax', 'near_attenuation'),
                          ('LightOmniMax', 'near_attenuation_start'), ('LightOmniMax', 'near_attenuation_end'),
                          ('LightOmniMax', 'far_attenuation'),
                          ('LightOmniMax', 'far_attenuation_start'), ('LightOmniMax', 'far_attenuation_end'),
                          ('RenderChannelBumpNormals', 'enableDeepOutput'),
                          ('RenderChannelDenoiser', 'enableDeepOutput'),
                          ('RenderChannelDRBucket', 'enableDeepOutput'), ('RenderChannelExtraTex', 'enableDeepOutput'),
                          ('RenderChannelNormals', 'enableDeepOutput'), ('RenderChannelNodeID', 'enableDeepOutput'),
                          ('RenderChannelRenderID', 'enableDeepOutput'), ('RenderChannelVelocity', 'enableDeepOutput'),
                          ('RenderChannelZDepth', 'enableDeepOutput'),
                          ('FilterLanczos', 'size'), ('FilterArea', 'size'), ('FilterGaussian', 'size'),
                          ('FilterCookVariable', 'size'), ('FilterSinc', 'size'), ('FilterBox', 'size'),
                          ('FilterTriangle', 'size'), ('FilterMitNet', 'size'), ('FilterMitNet', 'blur'),
                          ('FilterMitNet', 'ringing'),
                          ('BRDFVRayMtl', 'roughness_model'), ('BRDFVRayMtl', 'option_use_roughness'),
                          ('LightRectangle', 'lightPortal'), ('LightRectangle', 'units'),
                          ('LightRectangle', 'map_color'),
                          ('ColorCorrection', 'adv_exposure_mode'), ('ColorCorrection', 'adv_printer_lights_per'),
                          ('SettingsRTEngine', 'low_gpu_thread_priority'),
                          ('SettingsRTEngine', 'interactive'), ('SettingsRTEngine', 'enable_cpu_interop'),
                          ('SettingsUnitsInfo', 'meters_scale'),
                          ('SettingsUnitsInfo', 'photometric_scale'), ('SettingsUnitsInfo', 'scene_upDir'),
                          ('SettingsUnitsInfo', 'seconds_scale'), ('SettingsUnitsInfo', 'frames_scale'),
                          ('SettingsUnitsInfo', 'rgb_color_space'),
                          ('SettingsImageSampler', 'progressive_effectsUpdate'),
                          ('SettingsImageSampler', 'render_mask_clear'), ('SettingsLightCache', 'premultiplied'),
                          ('SettingsIrradianceMap', 'detail_enhancement'), ('SettingsPhotonMap', 'bounces'),
                          ('SettingsPhotonMap', 'file'), ('SettingsPhotonMap', 'max_photons'),
                          ('SettingsPhotonMap', 'prefilter'), ('SettingsPhotonMap', 'prefilter_samples'),
                          ('SettingsPhotonMap', 'mode'),
                          ('SettingsPhotonMap', 'auto_search_distance'), ('SettingsPhotonMap', 'search_distance'),
                          ('SettingsPhotonMap', 'convex_hull_estimate'), ('SettingsPhotonMap', 'dont_delete'),
                          ('SettingsPhotonMap', 'auto_save'),
                          ('SettingsPhotonMap', 'auto_save_file'), ('SettingsPhotonMap', 'store_direct_light'),
                          ('SettingsPhotonMap', 'multiplier'),
                          ('SettingsPhotonMap', 'max_density'), ('SettingsPhotonMap', 'retrace_corners'),
                          ('SettingsPhotonMap', 'retrace_bounces'),
                          ('SettingsPhotonMap', 'show_calc_phase'), ('SettingsDMCSampler', 'path_sampler_type'),
                          ('SettingsVFB', 'bloom_on'),
                          ('SettingsVFB', 'bloom_fill_edges'), ('SettingsVFB', 'bloom_weight'),
                          ('SettingsVFB', 'bloom_size'), ('SettingsVFB', 'bloom_shape'),
                          ('SettingsVFB', 'bloom_mode'), ('SettingsVFB', 'bloom_mask_intensity_on'),
                          ('SettingsVFB', 'bloom_mask_intensity'), ('SettingsVFB', 'bloom_mask_objid_on'),
                          ('SettingsVFB', 'bloom_mask_objid'), ('SettingsVFB', 'bloom_mask_mtlid_on'),
                          ('SettingsVFB', 'bloom_mask_mtlid'), ('SettingsVFB', 'glare_on'),
                          ('SettingsVFB', 'glare_fill_edges'), ('SettingsVFB', 'glare_weight'),
                          ('SettingsVFB', 'glare_size'), ('SettingsVFB', 'glare_type'), ('SettingsVFB', 'glare_mode'),
                          ('SettingsVFB', 'glare_image_path'), ('SettingsVFB', 'glare_obstacle_image_path'),
                          ('SettingsVFB', 'glare_diffraction_on'),
                          ('SettingsVFB', 'glare_use_obstacle_image'), ('SettingsVFB', 'glare_cam_blades_on'),
                          ('SettingsVFB', 'glare_cam_num_blades'),
                          ('SettingsVFB', 'glare_cam_rotation'), ('SettingsVFB', 'glare_cam_fnumber'),
                          ('SettingsVFB', 'glare_mask_intensity_on'),
                          ('SettingsVFB', 'glare_mask_intensity'), ('SettingsVFB', 'glare_mask_objid_on'),
                          ('SettingsVFB', 'glare_mask_objid'),
                          ('SettingsVFB', 'glare_mask_mtlid_on'), ('SettingsVFB', 'glare_mask_mtlid'),
                          ('SettingsVFB', 'interactive'),
                          ('SettingsVFB', 'hardware_accelerated'), ('SettingsVFB', 'display_srgb'),
                          ('TexDirt',
                           'subdivs_as_samples'))  # some black listed parameters, maybe not yet implemented or no need to be implemented...

    network_tab = \
        [pane for pane in hou.ui.paneTabs() if
         isinstance(pane, hou.NetworkEditor) and pane.isCurrentTab()][
            -1]

    def parse_vrscene_file(self, fname, plugins, cameras, lights, settings, renderChannels, nodes, environments,
                           geometries,
                           targetObjects, displacements):

        import re
        import os

        print '\n#############################################'
        print '##########  LOADING .VRSCENE FILE  ##########'
        print '#############################################'

        with open(fname, 'r') as content_file:
            content = content_file.read()

        matches = re.finditer(r'\#include\ \"(.*?)\"\n', content, re.MULTILINE | re.DOTALL)
        for matchNum, match in enumerate(matches):
            fname = match.group(1).strip()

            if os.path.isfile(fname):
                with open(fname, 'r') as content_file:
                    content += content_file.read()

        content = re.sub(re.compile('\#include\ \"(.*?)\"\n'), '', content)  # content without includes
        content = re.sub(re.compile('//.*?\n'), '', content)  # content without comments

        print content

        print '\n\n\n#############################################'
        print '###############  FILE PARSING  ##############'
        print '#############################################\n\n'
        print '\n\n\n'

        matches = re.finditer(r'(.*?)\ (.*?)\ \{(.*?)\}', content, re.MULTILINE | re.DOTALL)

        for matchNum, match in enumerate(matches):
            type = match.group(1).strip()

            # do not catch parameters from GeomStaticMesh !
            if type != 'GeomStaticMesh' and type != 'RenderView' and type != 'Filter':

                name = match.group(2).strip()
                parms = list()

                for p in (i for i in match.group(3).split(';') if i.strip() != ''):
                    split = p.strip().split('=', 1)
                    if len(split) == 2:
                        parm_name = split[0]

                        if not (type, parm_name) in self.black_listed_parms:
                            parm_val = split[1]
                            parms.append({'Name': parm_name, 'Value': parm_val})

                if type == 'Node':
                    nodes.append({'Type': type, 'Name': name, 'Parms': parms})

                # catch vray environment
                elif 'SettingsEnvironment' in type:
                    for p in parms:
                        if '_tex' in p['Name']:
                            environments.append(p)

                # catch vray render channels
                elif 'RenderChannel' in type:
                    renderChannels.append({'Type': type, 'Name': name, 'Parms': parms})

                # catch vray render settings
                # elif 'Settings' in type and type != 'SettingsCamera':
                elif 'Settings' in type or name == 'aaFilter':
                    settings.append({'Type': type, 'Name': name, 'Parms': parms})

                # catch lights
                elif 'Light' in type and not 'BRDFLight' in type:
                    lights.append({'Type': type, 'Name': name, 'Parms': parms})

                # catch cameras
                elif 'Camera' in type and not 'CameraPhysical' in type and not 'SettingsCamera' in type:
                    cameras.append({'Type': type, 'Name': name, 'Parms': parms})

                # catch target objects
                elif 'Target' in type:
                    targetObjects.append({'Type': type, 'Name': name, 'Parms': parms})

                # catch geometries
                elif 'Geometry' in type:
                    geometries.append({'Type': type, 'Name': name, 'Parms': parms})

                # catch displacements
                elif 'GeomDisplacedMesh' in type:
                    displacements.append({'Type': type, 'Name': name, 'Parms': parms})

                else:
                    # plugins.append({'Type': 'VRayNode' + type, 'Name': name, 'Parms': parms})
                    plugins.append({'Type': type, 'Name': name, 'Parms': parms})

    def normalize_name(self, name):
        return "_".join(filter(None, name.replace('@', '_').split('_')))

    def get_vray_rop_node(self):
        from vfh import vfh_rop

        vray_rop = vfh_rop._getVrayRop()

        if vray_rop == None:
            out = hou.node('/out')
            vray_rop = out.createNode('vray_renderer')

        return vray_rop

    def try_parse_parm_value(self, name, type, parm_name, parm_val, message_stack):
        import re

        result = parm_val

        try:
            if parm_val.startswith('"') and parm_val.endswith('"'):
                result = parm_val[1:-1]
                if type == 'UVWGenEnvironment' and parm_name == 'mapping_type':
                    if parm_val == 'mirror_ball':
                        result = 3
                    if parm_val == 'cubic':
                        result = 1
                    if parm_val == 'angular':
                        result = 3
                    if parm_val == 'spherical_vray':
                        result = 6

            elif parm_val.startswith('Keys'):
                # Transform(Matrix(Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)), Vector(0, 0, 0))
                result = re.match(r"Keys\((.*?.*)\)", parm_val)
                result = eval('(' + result.group(1).replace('Keys', '') + ')')

            elif parm_val.startswith('interpolate'):
                # TEMP !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                result = re.match(r"interpolate\((.*?.*)\)", parm_val, re.MULTILINE | re.DOTALL)
                result = hou.Matrix3(
                    (eval(result.group(1).replace('\n', '').replace('Vector', '').replace('Matrix', '').strip()))[1])

            elif parm_val.startswith('Matrix'):
                # Transform(Matrix(Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)), Vector(0, 0, 0))
                result = re.match(r"Matrix\((.*?.*)\)", parm_val)
                result = hou.Matrix3(eval('(' + result.group(1).replace('Vector', '') + ')'))

            elif parm_val.startswith('Transform'):
                # Transform(Matrix(Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)), Vector(0, 0, 0))
                result = re.match(r"Transform\(Matrix\((.*?.*)\), (.*?.*)\)", parm_val)
                result = (hou.Matrix3(eval('(' + result.group(1).replace('Vector', '') + ')')),
                          hou.Vector3(eval(result.group(2).replace('Vector', ''))))

            elif parm_val.startswith('Color'):
                result = hou.Vector3(eval(parm_val[5:]))

            elif parm_val.startswith('AColor'):
                result = hou.Vector4(eval(parm_val[6:]))

            elif parm_val.startswith('ListFloat'):
                result = (re.match(r"ListFloat\((.*?)\)", parm_val, re.MULTILINE | re.DOTALL)).group(
                    1).replace(' ', '').replace('\n', '').split(',')

            elif parm_val.startswith('ListInt'):
                result = (re.match(r"ListInt\((.*?)\)", parm_val, re.MULTILINE | re.DOTALL)).group(
                    1).replace(' ', '').replace('\n', '').split(',')

            elif parm_val.startswith('List'):
                # can be list of multiples types: AColor, int...

                if 'AColor' in parm_val:
                    matches = re.finditer(r"AColor\((.*?)\)", parm_val, re.MULTILINE | re.DOTALL)
                    result = list()
                    for matchNum, match in enumerate(matches):
                        acolor = 'AColor(' + match.group(1).strip() + ')'
                        result.append(acolor)

                elif 'Color' in parm_val:
                    matches = re.finditer(r"Color\((.*?)\)", parm_val, re.MULTILINE | re.DOTALL)
                    result = list()
                    for matchNum, match in enumerate(matches):
                        color = 'Color(' + match.group(1).strip() + ')'
                        result.append(color)

                else:
                    result = (re.match(r"List\((.*?)\)", parm_val, re.MULTILINE | re.DOTALL)).group(
                        1).replace(' ', '').replace('\n', '').split(',')

            elif parm_val.startswith('Vector'):
                result = hou.Vector3(eval(parm_val[6:]))

            else:
                result = eval(parm_val)

                if (type, parm_name) in self.metric_parms:
                    result /= 100

                if (type, parm_name) in self.deg_to_rad_parms:
                    import math
                    result /= math.radians(result)

        except:
            if not '@' in str(parm_val) and not 'bitmapBuffer' in str(parm_val):
                message_stack.append('Warning - cannot parsing value: ' + str(
                    parm_val) + ' on parameter: ' + parm_name + ' on node: ' + name)

        return result

    def try_set_parm(self, node, parm_name, parm_val, message_stack):
        try:
            if isinstance(parm_val, tuple):
                for k in parm_val:
                    setKey = hou.Keyframe()
                    setKey.setFrame(k[0])
                    setKey.setValue(k[1])
                    node.parm(parm_name).setKeyframe(setKey)

            elif isinstance(parm_val, hou.Vector3) or isinstance(parm_val, hou.Vector4):
                node.parmTuple(parm_name).set(parm_val)

            elif isinstance(parm_val, hou.Matrix3):
                node.parmTuple(parm_name).set(parm_val.asTuple())

            else:
                node.parm(parm_name).set(parm_val)

        except:
            message_stack.append('Cannot set parm on ' + node.type().name().replace('VRayNode',
                                                                                    '') + ' ( ' + node.name() + ' ) ' + parm_name + ' = ' + str(
                parm_val))

    def set_timeline_range(self, start, end):
        setGobalFrangeExpr = 'tset `(%d-1)/$FPS` `%d/$FPS`' % (start, end)
        hou.hscript(setGobalFrangeExpr)
        hou.playbar.setPlaybackRange(start, end)

    def format_value(self, value):
        result = str(value)
        if isinstance(value, (str, unicode)):
            result = '"' + str(value) + '"'
        return result

    def load_settings(self, settings):
        # loading settings
        message_stack = list()

        vray_rop = self.get_vray_rop_node()
        self.revert_parms_to_default(vray_rop.parms(),
                                     ('render_camera', 'render_network_render_channels', 'render_network_environment'))

        print '\n\n\n#############################################'
        print '#########  LOADING RENDER SETTINGS  #########'
        print '#############################################\n\n'

        for s in settings:

            if s['Name'] == 'aaFilter':
                filter_type = 0
                if s['Type'] == 'FilterArea':
                    filter_type = 1
                elif s['Type'] == 'FilterBox':
                    filter_type = 2
                elif s['Type'] == 'FilterCatmullRom':
                    filter_type = 3
                elif s['Type'] == 'FilterCookVariable':
                    filter_type = 4
                elif s['Type'] == 'FilterGaussian':
                    filter_type = 5
                elif s['Type'] == 'FilterLanczos':
                    filter_type = 6
                elif s['Type'] == 'FilterMitNet':
                    filter_type = 7
                elif s['Type'] == 'FilterSinc':
                    filter_type = 8
                elif s['Type'] == 'FilterTriangle':
                    filter_type = 9

                self.try_set_parm(vray_rop, 'SettingsImageSampler_filter_type', filter_type, message_stack)

            for p in s['Parms']:
                parm_name = p['Name']
                parm_val = self.try_parse_parm_value(s['Name'], s['Type'], parm_name, p['Value'], message_stack)

                print s['Type'] + '_' + parm_name + ' = ' + self.format_value(parm_val)

                if s['Type'] == 'CustomSettings':
                    if parm_name == 'name':
                        if parm_val != '':
                            hip_dir = hou.getenv('HIP')
                            hou.hipFile.setName(parm_val)
                            # self.set_environment_variable('JOB', hip_dir)
                            self.set_environment_variable('HIP', hip_dir)
                            self.set_environment_variable('HIPFILE', hip_dir + '/' + parm_val + '.hip')
                            self.set_environment_variable('HIPNAME', parm_val)

                    elif parm_name == 'camera':
                        cam = None
                        if parm_val == '':
                            cams = [child for child, child in enumerate(hou.node('/obj').children()) if
                                    child.type().name() == 'cam']
                            if len(cams) > 0:
                                cam = cams[0]
                        else:
                            cam = hou.node('/obj/' + parm_val)

                        if cam != None:
                            self.try_set_parm(vray_rop, 'render_camera', cam.path(), message_stack)
                            hou.ui.paneTabOfType(hou.paneTabType.SceneViewer).curViewport().setCamera(cam)

                    elif parm_name == 'fps':
                        hou.setFps(parm_val)
                    elif parm_name == 'range':
                        self.set_timeline_range(parm_val[0], parm_val[1])
                    elif parm_name == 'frame':
                        hou.setFrame(parm_val)

                else:
                    if s['Type'] == 'SettingsGI':
                        if parm_name == 'primary_engine' or parm_name == 'secondary_engine':
                            if parm_val == 2:
                                parm_val = 1
                            elif parm_val == 3:
                                parm_val = 2

                    self.try_set_parm(vray_rop, s['Type'] + '_' + parm_name, parm_val, message_stack)

        if len(message_stack) != 0:
            print '\n\n\nLoad Render Settings terminated with: ' + str(len(message_stack)) + ' errors:\n'
        else:
            print '\n\n\nLoad Render Settings terminated successfully\n'

        for m in message_stack:
            print m

    def init_constraint(self, node, target):
        constraints = node.createNode('chopnet', 'constraints')

        parm_group = constraints.parmTemplateGroup()
        parm_group.addParmTemplate(hou.IntParmTemplate('chopnet_rate', 'CHOP Rate', 1))
        parm_group.addParmTemplate(hou.IntParmTemplate('motionsamples', 'CHOP Motion Samples', 1))
        constraints.setParmTemplateGroup(parm_group)

        constraints.parm('chopnet_rate').setExpression('$FPS * ch("motionsamples")')
        constraints.parm('motionsamples').setExpression('$CHOPMOTIONSAMPLES')
        constraints.moveToGoodPosition()

        node.parm('constraints_on').set(1)
        node.parm('constraints_path').set('constraints')

        constraintlookat = constraints.createNode('constraintlookat', 'lookat')
        constraintlookat.parm('vex_range').set(1)
        constraintlookat.parm('vex_rate').setExpression('ch("../chopnet_rate")')
        constraintlookat.parm('export').set('../..')
        constraintlookat.parm('gcolorr').set(0)
        constraintlookat.parm('gcolorg').set(0)
        constraintlookat.parm('gcolorb').set(0.9)

        constraintgetworldspace = constraints.createNode('constraintgetworldspace', 'getworldspace')
        constraintgetworldspace.parm('obj_path').set('../..')
        constraintgetworldspace.parm('vex_range').set(1)
        constraintgetworldspace.parm('vex_rate').setExpression('ch("../chopnet_rate")')
        constraintgetworldspace.parm('export').set('../..')
        constraintgetworldspace.parm('gcolorr').set(0.9)
        constraintgetworldspace.parm('gcolorg').set(0)
        constraintgetworldspace.parm('gcolorb').set(0)

        constraintobject = constraints.createNode('constraintobject', 'target_node')
        constraintobject.parm('obj_path').setExpression('chsop("../../lookat_target")')
        constraintobject.parm('vex_range').set(1)
        constraintobject.parm('vex_rate').setExpression('ch("../chopnet_rate")')
        constraintobject.parm('export').set('../..')
        constraintobject.parm('gcolorr').set(0.9)
        constraintobject.parm('gcolorg').set(0.9)
        constraintobject.parm('gcolorb').set(0)

        constraintlookat.setInput(0, constraintgetworldspace)
        constraintlookat.setInput(1, constraintobject)
        constraints.layoutChildren()

    def try_find_or_create_target_object(self, parent, node, name, target_objects, message_stack):
        print '\n\n' + name + ' ( TargetObject ) \n'

        target = self.try_create_node(parent, 'null', name, message_stack)

        if target != None:

            parm_group = target.parmTemplateGroup()
            parm_group.insertBefore(parm_group.findFolder("Transform"),
                                    hou.StringParmTemplate('lookat_parent', 'Parent', 1,
                                                           string_type=hou.stringParmType.NodeReference))
            target.setParmTemplateGroup(parm_group)
            target.parm('lookat_parent').set(node.path())

            parm_group = node.parmTemplateGroup()
            parm_group.insertBefore(parm_group.findFolder("Transform"),
                                    hou.StringParmTemplate('lookat_target', 'Target', 1,
                                                           string_type=hou.stringParmType.NodeReference))

            node.setParmTemplateGroup(parm_group)
            node.parm('lookat_target').set(target.path())

            self.init_constraint(node, target)
            node.node('constraints').node('lookat').parm('twist').setExpression('ch("../../rz")')

            # target.parmTuple('dcolor').set(hou.Vector3(node.color().rgb()))
            target.parmTuple('dcolor').set(hou.Vector3())
            target.parm('geoscale').set(0.2)
            target.parm('controltype').set(2)
            target.setUserData('nodeshape', 'circle')
            target.setColor(node.color())
            target.setPosition(node.position() + hou.Vector2(0, -1))

            for t in target_objects:
                if t['Name'] == name:

                    for p in t['Parms']:
                        parm_val = self.try_parse_parm_value(name, 'TargetObject', p['Name'], p['Value'], message_stack)

                        print p['Name'] + " = " + str(parm_val)
                        self.try_set_parm(target, p['Name'], parm_val, message_stack)

                    break

    def collect_current_physical_camera_attributes(self, node):
        """
        Collects current CameraPhysical attribute values.
        """
        parms = dict()

        for pt in node.parmTemplateGroup().entries():
            attrName = pt.name()
            if attrName.startswith("CameraPhysical_"):
                try:
                    p = node.parm(attrName)
                    parms[attrName] = p.eval()
                except:
                    pass

        return parms

    def remove_current_physical_camera_attributes(self, node, folderLabel):
        """
        Removes existing CameraPhysical attributes.
        """
        ptg = node.parmTemplateGroup()

        folder = ptg.findFolder(folderLabel)
        if folder:
            ptg.remove(folder.name())

        # Removing the folder doesn't remove invisible parameters
        for pt in ptg.entries():
            attrName = pt.name()
            if attrName.startswith("CameraPhysical"):
                ptg.remove(attrName)

        node.setParmTemplateGroup(ptg)

    def add_physical_camera_attributes(self, node):
        import os
        import sys
        UI = os.environ.get('VRAY_UI_DS_PATH', None)

        if UI is None:
            return

        physCamDS = os.path.join(UI, "plugins", "CameraPhysical.ds")
        if not os.path.exists(physCamDS):
            sys.stderr.write("CameraPhysical.ds is not found!\n")
            return

        if node.type().name() in {"cam"}:

            folderName = "VfhCameraPhysical"
            folderLabel = "V-Ray Physical Camera"

            currentSettings = self.collect_current_physical_camera_attributes(node)

            self.remove_current_physical_camera_attributes(node, folderLabel)

            group = node.parmTemplateGroup()
            folder = hou.FolderParmTemplate(folderName, folderLabel)

            physCamGroup = hou.ParmTemplateGroup()
            physCamGroup.setToDialogScript(open(physCamDS, 'r').read())
            for parmTmpl in physCamGroup.parmTemplates():
                folder.addParmTemplate(parmTmpl)

            group.append(folder)
            node.setParmTemplateGroup(group)

            for parm in node.parms():
                try:
                    attrName = parm.name()

                    parmValue = currentSettings.get(attrName, None)
                    if parmValue is not None:
                        parm.set(parmValue)
                    elif attrName in {"CameraPhysical_f_number"}:
                        parm.setExpression("ch(\"./fstop\")")
                    elif attrName in {"CameraPhysical_focus_distance"}:
                        parm.setExpression("ch(\"./focus\")")
                    elif attrName in {"CameraPhysical_horizontal_offset"}:
                        parm.setExpression("-ch(\"./winx\")")
                    elif attrName in {"CameraPhysical_vertical_offset"}:
                        parm.setExpression("-ch(\"./winy\")")
                    elif attrName in {"CameraPhysical_focal_length"}:
                        parm.setExpression("ch(\"./focal\")")
                    elif attrName in {"CameraPhysical_film_width"}:
                        parm.setExpression("ch(\"./aperture\")")
                except:
                    pass

    def load_cameras(self, cameras, target_objects):
        # loading settings
        message_stack = list()
        obj = hou.node('/obj')

        print '\n\n\n#############################################'
        print '#############  LOADING CAMERAS  #############'
        print '#############################################\n\n'

        for c in cameras:

            print c['Name'] + ' ( ' + c['Type'] + ' ) \n'

            camera = self.try_create_node(obj, 'cam', c['Name'], message_stack)

            if camera != None:
                for p in c['Parms']:
                    parm_name = p['Name']
                    parm_val = self.try_parse_parm_value(c['Name'], c['Type'], parm_name, p['Value'], message_stack)

                    if parm_name == 'target':
                        self.try_find_or_create_target_object(obj, camera, parm_val, target_objects, message_stack)
                    elif parm_name == 'CameraPhysical_use':
                        if parm_val == True:
                            self.add_physical_camera_attributes(camera)
                    else:
                        print parm_name + " = " + str(parm_val)
                        self.try_set_parm(camera, parm_name, parm_val, message_stack)

            print '\n\n'

        if len(message_stack) != 0:
            print '\n\n\nLoad Cameras terminated with: ' + str(len(message_stack)) + ' errors:\n'
        else:
            print '\n\n\nLoad Cameras terminated successfully\n'

        for m in message_stack:
            print m

    def load_lights(self, lights, target_objects):
        # loading settings
        message_stack = list()
        obj = hou.node('/obj')

        print '\n\n\n#############################################'
        print '##############  LOADING LIGHTS  #############'
        print '#############################################\n\n'

        for l in lights:

            # particular case for suffixed 'Max' types, need conversion
            if l['Type'] == 'LightOmniMax':
                l['Type'] = 'LightOmni'
            elif l['Type'] == 'LightAmbientMax':
                l['Type'] = 'LightAmbient'
            elif l['Type'] == 'LightIESMax':
                l['Type'] = 'LightIES'
            elif l['Type'] == 'LightSpotMax':
                l['Type'] = 'LightSpot'
            elif l['Type'] == 'LightDirectMax':
                l['Type'] = 'LightDirect'

            print l['Name'] + ' ( ' + l['Type'] + ' ) \n'

            name = l['Name'].split('@', 1)[0]

            light = self.try_create_node(obj, 'VRayNode' + l['Type'], name, message_stack)

            if light != None:
                light.setColor(hou.Color(1, 0.898039, 0))
                light.setUserData('nodeshape', 'light')

                for p in l['Parms']:
                    parm_name = p['Name']
                    parm_val = self.try_parse_parm_value(l['Name'], l['Type'], parm_name, p['Value'], message_stack)

                    # if parm_name == 'target':
                    #    self.try_find_or_create_target_object(obj, light, parm_val, target_objects, message_stack)
                    if parm_name == 'transform':
                        try:
                            result = hou.Matrix4(parm_val[0]).explode(transform_order='trs', rotate_order='xyz',
                                                                      pivot=hou.Vector3(0.5, 0.5, 0))  # TEST

                            t = parm_val[1] * 0.01
                            t = hou.Vector3([t[0], t[2], -t[1]])

                            r = result['rotate']
                            r = hou.Vector3([r[0] - 90, r[2], r[1]])

                            p = result['shear']

                            self.try_set_parm(light, 't', t, message_stack)
                            self.try_set_parm(light, 'r', r, message_stack)
                            # self.try_set_parm(light, 's', result['scale'], message_stack)
                            self.try_set_parm(light, 'p', p, message_stack)
                        except:
                            message_stack.append('Cannot extract matrix4 transforms...')

                    else:
                        print parm_name + " = " + str(parm_val)
                        self.try_set_parm(light, parm_name, parm_val, message_stack)

            print '\n\n'

        if len(message_stack) != 0:
            print '\n\n\nLoad Lights terminated with: ' + str(len(message_stack)) + ' errors:\n'
        else:
            print '\n\n\nLoad Lights terminated successfully\n'

        for m in message_stack:
            print m

    def get_render_channels_container(self, render_channels_rop):
        render_channel_container = None
        result = [child for child in render_channels_rop.children() if
                  child.type().name() == 'VRayNodeRenderChannelsContainer']

        if len(result) > 0:
            render_channel_container = result[0]
        else:
            render_channel_container = render_channels_rop.createNode('VRayNodeRenderChannelsContainer')
            render_channel_container.moveToGoodPosition()
        return render_channel_container

    def try_create_node(self, parent, type, name, message_stack):
        node = None
        old_node = parent.node(name)

        try:
            node = parent.createNode(type)
            if old_node != None:
                node.setPosition(old_node.position())
            else:
                node.moveToGoodPosition()
        except:
            message_stack.append(
                'cannot create node name:' + name + ' type: ' + str(type) + ' parent: ' + parent.name())

        if node != None:
            if old_node != None:
                old_node.destroy()
            try:
                node.setName(name)
            except:
                message_stack.append('cannot set name:' + name)

        return node

    def try_find_or_create_node(self, parent, type, name, message_stack):
        node = parent.node(name)

        if node != None:
            for p in (node.parms()):
                p.deleteAllKeyframes()
        else:
            try:
                node = parent.createNode(type)
                node.moveToGoodPosition()
            except:
                message_stack.append(
                    'cannot create node name:' + name + ' type: ' + str(type) + ' parent: ' + parent.name())

            if node != None:
                try:
                    node.setName(name)
                except:
                    message_stack.append('cannot set name:' + name)

        return node

    def load_render_channels(self, plugins, renderChannels):
        # loading render channels
        message_stack = list()

        vray_rop = self.get_vray_rop_node()
        render_elements = hou.node(vray_rop.parm('render_network_render_channels').eval())

        if render_elements == None:
            out = hou.node('/out')
            render_elements = out.createNode('vray_render_channels', 'render_elements')
            render_elements.moveToGoodPosition()
            vray_rop.parm('render_network_render_channels').set(render_elements.path())

        for child in render_elements.children():
            if child.type().name() != 'VRayNodeRenderChannelsContainer':
                child.destroy()

        output_node = self.get_render_channels_container(render_elements)

        print '\n\n\n#############################################'
        print '#########  LOADING RENDER CHANNELS  #########'
        print '#############################################\n\n'

        for s in renderChannels:

            name = s['Name'].split('@', 1)[0]
            type = s['Type']

            print name + ' ( ' + s['Type'] + ' ) \n'

            node = self.try_create_node(render_elements, 'VRayNode' + s['Type'], name, message_stack)

            if node != None:
                output_node.setNextInput(node)

                for p in s['Parms']:
                    parm_name = p['Name']
                    parm_val = self.try_parse_parm_value(s['Name'], s['Type'], parm_name, p['Value'], message_stack)

                    if type == 'RenderChannelColor' and parm_name == 'alias':
                        parm_val -= 100  # item numbering from max starts at 100

                    if parm_name == 'texmap':
                        for nn in plugins:
                            if nn['Name'] == str(parm_val):
                                self.add_plugin_node(plugins, render_elements, node, parm_name,
                                                     self.normalize_name(nn['Name']),
                                                     nn['Type'], nn['Parms'], message_stack)


                    else:

                        print parm_name + " = " + str(parm_val)

                        self.try_set_parm(node, parm_name, parm_val, message_stack)

                print '\n\n'

        self.auto_arrange_children(render_elements)

        if len(message_stack) != 0:
            print '\n\n\nLoad Render Channels terminated with: ' + str(len(message_stack)) + ' errors:\n'
        else:
            print '\n\n\nLoad Render Channels terminated successfully\n'

        for m in message_stack:
            print m

    def add_vray_objectid_param_template(self, geo):
        parm_group = geo.parmTemplateGroup()
        parm_folder = hou.FolderParmTemplate('folder', 'V-Ray Object')
        parm_folder.addParmTemplate(hou.IntParmTemplate('vray_objectID', 'Object ID', 1))
        parm_group.append(parm_folder)
        geo.setParmTemplateGroup(parm_group)

    def add_scene_wirecolor_visualizer(self):
        if len([visualizer for visualizer in
                hou.viewportVisualizers.visualizers(category=hou.viewportVisualizerCategory.Scene) if
                visualizer.name() == 'wirecolor']) == 0:
            wirecolor_vis = hou.viewportVisualizers.createVisualizer(hou.viewportVisualizers.types()[1],
                                                                     category=hou.viewportVisualizerCategory.Scene)
            wirecolor_vis.setName('wirecolor')
            wirecolor_vis.setLabel('Wirecolor')
            wirecolor_vis.setParm('attrib', 'wirecolor')
            wirecolor_vis.setParm('class', 3)
            geoviewport = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer).curViewport()
            wirecolor_vis.setIsActive(True, viewport=geoviewport)

    def load_nodes(self, nodes, geometries, materials, displacements, plugins):
        import os
        import shutil
        from os.path import basename

        # loading nodes
        message_stack = list()
        obj = hou.node('/obj')

        # geo_dir = hou.expandString('$HIP') + '/geo/'
        geo_dir = hou.getenv('HIP') + '/geo/'

        print '\n\n\n#############################################'
        print '###########  LOADING SCENE NODES  ###########'
        print '#############################################\n\n'

        for n in nodes:
            name = n['Name'].split('@', 1)[0]
            material = n['Parms'][[i for i, s in enumerate(n['Parms']) if 'material' in s['Name']][0]]['Value']

            material_name = self.normalize_name(material.split('@', 1)[0])
            materials.append({'Name': material_name, 'Codename': material})

            displacement = None
            displacement_name = n['Parms'][[i for i, s in enumerate(n['Parms']) if 'geometry' in s['Name']][0]]['Value']
            if 'mesh_displaced' in displacement_name:
                for d in displacements:
                    if d['Name'] == displacement_name:
                        displacement = d
                        break

            # here search for the corresponding geometry
            geometry = None
            for g in geometries:
                if g['Name'] == name:
                    geometry = g
                    break

            # if geometry exists getting parameters...
            if geometry != None:
                geo = self.try_create_node(obj, 'geo', self.normalize_name(name), message_stack)

                if geo != None:
                    for child in geo.children():
                        child.destroy()

                    self.add_vray_objectid_param_template(geo)
                    geo.parm('shop_materialpath').set('/shop/' + material_name)

                    if displacement != None:
                        # displacement_tex_color
                        # displacement_amount
                        import vfh.shelftools.vrayattr as vrayattr
                        HOUDINI_SOHO_DEVELOPER = os.environ.get("HOUDINI_SOHO_DEVELOPER", False)
                        if HOUDINI_SOHO_DEVELOPER:
                            reload(vrayattr)
                        vrayattr.addVRayDisplamentParams(geo)
                        for p in displacement['Parms']:
                            parm_name = p['Name']
                            parm_val = p['Value']

                            if parm_name == 'displacement_tex_color':
                                # load texture map here...

                                parent = geo.createNode('matnet', 'displacement')
                                output_node = None
                                for nn in plugins:
                                    if nn['Name'] == str(parm_val):
                                        self.add_plugin_node(plugins, parent, output_node, parm_name,
                                                             self.normalize_name(nn['Name']),
                                                             nn['Type'], nn['Parms'], message_stack)

                                    geo.parm('GeomDisplacedMesh_displacement_texture').set(
                                        '`chs("displacement/' + self.normalize_name(nn['Name']) + '")`')  # TEMP...

                                parent.layoutChildren()

                            else:
                                parm_val = self.try_parse_parm_value(name, n['Type'], parm_name, parm_val,
                                                                     message_stack)
                                self.try_set_parm(geo, 'GeomDisplacedMesh_' + parm_name, parm_val, message_stack)

                # retrieving geometry parameters
                from_filename = ''
                object_id = 0
                wirecolor = (0.5, 0.5, 0.5)
                handle = 0
                for p in geometry['Parms']:
                    parm_name = p['Name']
                    parm_val = p['Value']

                    if parm_name == 'filename':
                        from_filename = self.try_parse_parm_value(name, n['Type'], parm_name, parm_val, message_stack)
                    elif parm_name == 'object_id':
                        object_id = self.try_parse_parm_value(name, n['Type'], parm_name, parm_val, message_stack)
                    elif parm_name == 'wirecolor':
                        wirecolor = self.try_parse_parm_value(name, n['Type'], parm_name, parm_val, message_stack)
                    elif parm_name == 'handle':
                        handle = self.try_parse_parm_value(name, n['Type'], parm_name, parm_val, message_stack)
                    else:
                        # transform values
                        parm_val = self.try_parse_parm_value(name, n['Type'], parm_name, parm_val, message_stack)
                        self.try_set_parm(geo, parm_name, parm_val, message_stack)

                # copy cache file from temp location to .hip/geo dir
                if os.path.isfile(from_filename):
                    to_filename = geo_dir + basename(from_filename)  # + ".abc"
                    try:
                        # shutil.move(from_filename, to_filename)
                        shutil.copy(from_filename, to_filename)
                    except IOError:
                        os.chmod(to_filename, 777)  # ?? still can raise exception
                        shutil.move(from_filename, to_filename)
                        message_stack.append('Cannot copy .abc file...')

                geo.parm('vray_objectID').set(object_id)
                geo.parm('use_dcolor').set(True)
                geo.parm('dcolorr').set(wirecolor[0])
                geo.parm('dcolorg').set(wirecolor[1])
                geo.parm('dcolorb').set(wirecolor[2])

                alembic = geo.node('alembic1')
                if alembic == None:
                    alembic = geo.createNode('alembic')
                alembic.parm('fileName').set('$HIP/geo/' + basename(from_filename))  # + ".abc")
                alembic.parm('reload').pressButton()

                xform = geo.node('xform1')
                if xform == None:
                    xform = alembic.createOutputNode('xform', 'xform1')
                xform.parm('scale').set(0.01)

                properties = geo.node('properties')
                if properties == None:
                    properties = xform.createOutputNode('attribwrangle', 'properties')
                    properties.parm('class').set(0)
                    properties.setDisplayFlag(True)

                properties.parm('snippet').set(
                    'v@wirecolor = set(' + str(wirecolor[0]) + ', ' + str(wirecolor[1]) + ', ' + str(
                        wirecolor[2]) + ');\ni@handle = ' + str(handle) + ';')

                vraypoxy = geo.node('vrayproxy1')
                if vraypoxy == None:
                    vraypoxy = geo.createNode('VRayNodeVRayProxy', 'vrayproxy1')
                    vraypoxy.moveToGoodPosition()

                vraypoxy.parm('file').setExpression('chs("../alembic1/fileName")')
                vraypoxy.parm('reload').pressButton()
                vraypoxy.parm('scale').setExpression('ch("../xform1/scale")')
                vraypoxy.parm('first_map_channel').set(1)
                vraypoxy.setRenderFlag(True)

                geo.layoutChildren()

            print name + ' ( ' + material_name + ' )'

        self.add_scene_wirecolor_visualizer()

        if len(message_stack) != 0:
            print '\n\n\nLoad Scene Nodes terminated with: ' + str(len(message_stack)) + ' errors:\n'
        else:
            print '\n\n\nLoad Scene Nodes terminated successfully\n'

        for m in message_stack:
            print m

    def get_material_output(self, material):
        material_output = None
        result = [child for child in material.children() if child.type().name() == 'vray_material_output']
        if len(result) > 0:
            material_output = result[0]
        else:
            material_output = material.createNode('vray_material_output')
            material_output.moveToGoodPosition()
        return material_output

    def revert_parms_to_default(self, parms, exclude_parm_list=()):
        for i in range(len(parms), 0, -1):
            if not parms[i - 1].name() in exclude_parm_list:
                parms[i - 1].revertToDefaults()

    def try_set_input(self, output_node, input_name, node, message_stack, output_name=''):
        output_index = 0
        if output_name != '':
            result = node.outputIndex(output_name)
            if result != -1:
                output_index = result

        if output_node != None:
            input_index = output_node.inputIndex(input_name)

            if input_index != -1:
                try:
                    output_node.setInput(input_index, node, output_index)
                except:
                    message_stack.append('cannot set input: ' + str(
                        input_name) + ' from node: ' + output_node.name() + ' to node: ' + node.name())
            else:
                message_stack.append('cannot find input: ' + str(input_name) + ' on node: ' + output_node.name())

    def add_plugin_node(self, plugins, parent, output_node, input_name, node_name, node_type, node_parms,
                        message_stack, output_name=''):

        '''if node_type == 'TexBezierCurveColor':
            node_type = 'TexBezierCurve'''

        node = self.try_find_or_create_node(parent, 'VRayNode' + node_type, self.normalize_name(node_name),
                                            message_stack)

        print '\n\n( ' + self.normalize_name(node_name) + ' )'

        if node != None:

            self.try_set_input(output_node, input_name, node, message_stack, output_name)

            for p in node_parms:
                parm_name = p['Name']
                parm_val = self.try_parse_parm_value(node_name, node_type, parm_name, p['Value'], message_stack)

                if node_type == 'BRDFBump' and parm_name == 'bump_tex':
                    parm_name = 'bump_tex_color'  # to test !...

                if node_type == 'BitmapBuffer' and parm_name == 'interpolation':
                    if parm_val == 3: parm_val = 0  # need this conversion because of out of range error with value of 3

                if node_type == 'BRDFVRayMtl' and parm_name == 'brdf_type':
                    if parm_val == 4: parm_val = 3  # need this conversion because of the difference between max and houdini menu list

                if node_type == 'UVWGenEnvironment' and parm_name == 'mapping_type':
                    if parm_val == 'angular':
                        parm_val = 0
                    elif parm_val == 'cubic':
                        parm_val = 1
                    elif parm_val == 'spherical_vray':
                        parm_val = 6
                    elif parm_val == 'mirror_ball':
                        parm_val = 3
                    else:
                        message_stack.append(
                            'unknown mapping_type value: "' + str(parm_val) + '" on node: ' + node.name())
                        parm_val = 2

                if parm_name == 'uvw_transform':

                    makexform = self.try_find_or_create_node(parent, 'makexform', node.name() + '_transform',
                                                             message_stack)

                    if makexform != None:

                        try:
                            result = hou.Matrix4(parm_val[0]).explode(transform_order='trs', rotate_order='xyz',
                                                                      pivot=hou.Vector3(0.5, 0.5, 0))  # TEST

                            self.try_set_parm(makexform, 'trans', parm_val[1], message_stack)
                            self.try_set_parm(makexform, 'rot', result['rotate'], message_stack)
                            self.try_set_parm(makexform, 'scale', result['scale'], message_stack)
                            self.try_set_parm(makexform, 'pivot', result['shear'], message_stack)
                        except:
                            message_stack.append('Cannot extract matrix4 transforms...')

                        self.try_set_input(node, 'uvw_transform', makexform, message_stack)

                elif parm_name == 'uvw_matrix':

                    matrix = self.try_find_or_create_node(parent, 'parameter', node.name() + '_matrix', message_stack)

                    if matrix != None:
                        '''(preRotateX(matrix3[1, 0, 0][0, 0, 1][0, -1, 0][0, 0, 0]) - 90) * _t * inverse(
                            matrix3[1, 0, 0][0, 0, 1][0, -1, 0][0, 0, 0])'''

                        # matrix.setSelected(True)

                        self.try_set_parm(matrix, 'parmname', 'uvw_matrix', message_stack)
                        self.try_set_parm(matrix, 'parmtype', 13, message_stack)

                        try:
                            rot = parm_val.extractRotates()
                            quat = hou.Quaternion(hou.hmath.buildRotate((rot[0] - 90, -rot[2], rot[1]), "xyz"))
                            m3 = quat.extractRotationMatrix3().transposed()
                            self.try_set_parm(matrix, 'float9def', m3, message_stack)
                        except:
                            message_stack.append('Cannot extract matrix3 rotations...')

                        self.try_set_parm(matrix, 'invisible', 1, message_stack)
                        self.try_set_parm(matrix, 'exportparm', 1, message_stack)

                        self.try_set_input(node, 'uvw_matrix', matrix, message_stack)

                        # matrix.setSelected(False)
                        self.network_tab.cd(node.path())  # TEST
                        matrix.setSelected(True)
                        matrix.setSelected(False)

                elif node_type == 'MtlMulti':

                    if parm_name == 'mtls_list':
                        empty_material = self.try_find_or_create_node(parent, 'VRayNodeMtlDiffuse',
                                                                      node.name() + '_emty_mtl', message_stack)

                        material_id = self.try_find_or_create_node(parent, 'VRayNodeTexSampler',
                                                                   node.name() + '_mtlid_gen',
                                                                   message_stack)

                        if material_id != None:
                            # material_id.setSelected(True)

                            self.try_set_parm(node, 'mtl_count', len(parm_val), message_stack)

                            self.try_set_input(node, 'mtlid_gen_float', material_id, message_stack, 'material_id')
                            material_id.setGenericFlag(hou.nodeFlag.InOutDetailLow, True)
                            # material_id.setSelected(False)

                        for i in range(0, len(parm_val)):
                            self.try_set_input(node, 'mtl_' + str(i + 1), empty_material, message_stack)

                            for nn in plugins:
                                if nn['Name'] == parm_val[i]:
                                    self.add_plugin_node(plugins, parent, node, 'mtl_' + str(i + 1), nn['Name'],
                                                         nn['Type'],
                                                         nn['Parms'], message_stack)

                        if len(empty_material.outputs()) == 0:
                            empty_material.destroy()

                    elif parm_name == 'ids_list':

                        pass

                elif node_type == 'BRDFLayered':

                    if parm_name == 'brdfs':

                        self.try_set_parm(node, 'brdf_count', len(parm_val), message_stack)

                        parm_val = parm_val[::-1]  # reversed

                        for i in range(0, len(parm_val)):
                            for nn in plugins:
                                if nn['Name'] == parm_val[i]:
                                    self.add_plugin_node(plugins, parent, node, 'brdf_' + str(i + 1), nn['Name'],
                                                         nn['Type'],
                                                         nn['Parms'], message_stack)

                    elif parm_name == 'weights':

                        parm_val = parm_val[::-1]  # reversed

                        for i in range(0, len(parm_val)):
                            for nn in plugins:
                                if nn['Name'] == parm_val[i]:
                                    self.add_plugin_node(plugins, parent, node, 'weight_' + str(i + 1), nn['Name'],
                                                         nn['Type'],
                                                         nn['Parms'], message_stack)

                elif node_type == 'TexLayeredMax':
                    if parm_name == 'textures':
                        self.try_set_parm(node, 'textures_count', len(parm_val), message_stack)

                        # parm_val = parm_val[::-1]  # reversed
                        for i in range(0, len(parm_val)):
                            for nn in plugins:
                                if nn['Name'] == parm_val[i]:
                                    self.add_plugin_node(plugins, parent, node, 'tex_' + str(i + 1), nn['Name'],
                                                         nn['Type'],
                                                         nn['Parms'], message_stack)

                    elif parm_name == 'masks':
                        # use 'VRayNodeTexMaskMax' > inputs: 'texture', 'mask'
                        # if not 'whiteMask'...
                        # parm_val = parm_val[::-1]  # reversed
                        for i in range(0, len(parm_val)):
                            if parm_val[i] != 'whiteMask':
                                mask = self.try_find_or_create_node(parent, 'VRayNodeTexMaskMax', node.name() + '_mask',
                                                                    message_stack)

                                if mask != None:
                                    for nn in plugins:
                                        if nn['Name'] == parm_val[i]:
                                            self.add_plugin_node(plugins, parent, mask, 'mask', nn['Name'], nn['Type'],
                                                                 nn['Parms'], message_stack)

                                    tex_input_index = node.inputIndex('tex_' + str(i + 1))
                                    tex_node = node.inputs()[tex_input_index]

                                    if tex_node != None:
                                        self.try_set_input(mask, 'texture', tex_node, message_stack)

                                    self.try_set_input(node, 'tex_' + str(i + 1), mask, message_stack)

                    elif parm_name == 'blend_modes':
                        # parm_val = parm_val[::-1]  # reversed
                        for i in range(0, len(parm_val)):
                            self.try_set_parm(node, 'tex' + str(i + 1) + 'blend_mode', parm_val[i], message_stack)

                    elif parm_name == 'opacities':
                        # parm_val = parm_val[::-1]  # reversed
                        for i in range(0, len(parm_val)):
                            self.try_set_parm(node, 'tex' + str(i + 1) + 'blend_amount', parm_val[i], message_stack)

                elif node_type == 'TexMulti':
                    if parm_name == 'ids_list':
                        self.try_set_parm(node, 'textures_count', len(parm_val), message_stack)

                        # parm_val = parm_val[::-1]  # reversed
                        for i in range(0, len(parm_val)):
                            for nn in plugins:
                                if nn['Name'] == parm_val[i]:
                                    self.add_plugin_node(plugins, parent, node, 'tex_' + str(i + 1), nn['Name'],
                                                         nn['Type'],
                                                         nn['Parms'], message_stack)

                    elif parm_name == 'masks':
                        # use 'VRayNodeTexMaskMax' > inputs: 'texture', 'mask'
                        # if not 'whiteMask'...
                        # parm_val = parm_val[::-1]  # reversed
                        for i in range(0, len(parm_val)):
                            if parm_val[i] != 'whiteMask':
                                mask = self.try_find_or_create_node(parent, 'VRayNodeTexMaskMax', node.name() + '_mask',
                                                                    message_stack)

                                if mask != None:
                                    for nn in plugins:
                                        if nn['Name'] == parm_val[i]:
                                            self.add_plugin_node(plugins, parent, mask, 'mask', nn['Name'], nn['Type'],
                                                                 nn['Parms'], message_stack)

                                    tex_input_index = node.inputIndex('tex_' + str(i + 1))
                                    tex_node = node.inputs()[tex_input_index]

                                    if tex_node != None:
                                        self.try_set_input(mask, 'texture', tex_node, message_stack)

                                    self.try_set_input(node, 'tex_' + str(i + 1), mask, message_stack)

                    elif parm_name == 'blend_modes':
                        # parm_val = parm_val[::-1]  # reversed
                        for i in range(0, len(parm_val)):
                            self.try_set_parm(node, 'tex' + str(i + 1) + 'blend_mode', parm_val[i], message_stack)

                    elif parm_name == 'opacities':
                        # parm_val = parm_val[::-1]  # reversed
                        for i in range(0, len(parm_val)):
                            self.try_set_parm(node, 'tex' + str(i + 1) + 'blend_amount', parm_val[i], message_stack)

                elif node_type == 'TexGradRamp' and parm_name == 'positions':

                    # positions=ListFloat(0, 1, 0.92, 0.95);

                    # init ramp with default values (
                    count = len(parm_val)
                    rampData = hou.Ramp([hou.rampBasis.Linear] * count, [x * 1. / (count - 1) for x in range(0, count)],
                                        [(0.0, 0.0, 0.0)] * count)
                    try:
                        node.setParms({'color_ramp': rampData})
                    except:
                        message_stack.append('Cannot setting color_ramp...')
                    # ) end init ramp

                    for i in range(0, len(parm_val)):
                        parm_name = 'color_ramp' + str(i + 1) + 'pos'
                        pos = self.try_parse_parm_value(node_name, node_type, parm_name, parm_val[i], message_stack)
                        self.try_set_parm(node, parm_name, pos, message_stack)

                elif node_type == 'TexGradRamp' and parm_name == 'colors':
                    # colors = List(
                    #     Map__14 @ tex_10_0,
                    #     Map__14 @ tex_10_1,
                    #     Map__14 @ tex_10_2,
                    #     Map__14 @ tex_10_3
                    # );

                    for i in range(0, len(parm_val)):
                        parm_name = 'color_ramp' + str(i + 1) + 'c'
                        for nn in plugins:
                            if nn['Name'] == parm_val[i]:
                                c = self.try_parse_parm_value(nn['Name'], nn['Type'], nn['Parms'][0]['Name'],
                                                              nn['Parms'][0]['Value'], message_stack)
                                c = hou.Vector3((c.x(), c.y(), c.z()))  # Vector4 to Vector3
                                self.try_set_parm(node, parm_name, c, message_stack)
                                break

                elif node_type == 'TexGradRamp' and parm_name == 'interpolation':
                    # interpolation = ListInt(
                    #     1, 1, 1, 1);

                    for i in range(0, len(parm_val)):
                        parm_name = 'color_ramp' + str(i + 1) + 'interp'
                        interp = self.try_parse_parm_value(node_name, node_type, parm_name, parm_val[i], message_stack)
                        self.try_set_parm(node, parm_name, interp, message_stack)

                elif node_type == 'TexSoftbox' and parm_name == 'grad_vert_pos':
                    # grad_vert_pos = ['0', '1']

                    # init ramp with default values (
                    count = len(parm_val)
                    rampData = hou.Ramp([hou.rampBasis.Linear] * count, [x * 1. / (count - 1) for x in range(0, count)],
                                        [(0.0, 0.0, 0.0)] * count)
                    try:
                        node.setParms({'ramp_grad_vert': rampData})
                    except:
                        message_stack.append('Cannot setting color_ramp...')
                        # ) end init ramp

                    for i in range(0, len(parm_val)):
                        parm_name = 'ramp_grad_vert' + str(i + 1) + 'pos'
                        pos = self.try_parse_parm_value(node_name, node_type, parm_name, parm_val[i], message_stack)
                        self.try_set_parm(node, parm_name, pos, message_stack)

                elif node_type == 'TexSoftbox' and parm_name == 'grad_vert_col':
                    # grad_vert_col = ['AColor(0', '1', '0.9882354', '1']

                    for i in range(0, len(parm_val)):
                        parm_name = 'ramp_grad_vert' + str(i + 1) + 'c'
                        c = self.try_parse_parm_value(node_name, node_type, parm_name, parm_val[i], message_stack)
                        c = hou.Vector3((c.x(), c.y(), c.z()))  # Vector4 to Vector3
                        self.try_set_parm(node, parm_name, c, message_stack)

                elif node_type == 'TexSoftbox' and parm_name == 'grad_horiz_pos':
                    # grad_horiz_pos = ['0', '1']

                    # init ramp with default values (
                    count = len(parm_val)
                    rampData = hou.Ramp([hou.rampBasis.Linear] * count, [x * 1. / (count - 1) for x in range(0, count)],
                                        [(0.0, 0.0, 0.0)] * count)
                    try:
                        node.setParms({'ramp_grad_horiz': rampData})
                    except:
                        message_stack.append('Cannot setting color_ramp...')
                        # ) end init ramp

                    for i in range(0, len(parm_val)):
                        parm_name = 'ramp_grad_horiz' + str(i + 1) + 'pos'
                        pos = self.try_parse_parm_value(node_name, node_type, parm_name, parm_val[i], message_stack)
                        self.try_set_parm(node, parm_name, pos, message_stack)

                elif node_type == 'TexSoftbox' and parm_name == 'grad_horiz_col':
                    # grad_horiz_col = ['AColor(0', '1', '0.9882354', '1']

                    for i in range(0, len(parm_val)):
                        parm_name = 'ramp_grad_horiz' + str(i + 1) + 'c'
                        c = self.try_parse_parm_value(node_name, node_type, parm_name, parm_val[i], message_stack)
                        c = hou.Vector3((c.x(), c.y(), c.z()))  # Vector4 to Vector3
                        self.try_set_parm(node, parm_name, c, message_stack)

                elif node_type == 'TexSoftbox' and parm_name == 'grad_rad_pos':
                    # grad_rad_pos = ['0', '1']

                    # init ramp with default values (
                    count = len(parm_val)
                    rampData = hou.Ramp([hou.rampBasis.Linear] * count, [x * 1. / (count - 1) for x in range(0, count)],
                                        [(0.0, 0.0, 0.0)] * count)
                    try:
                        node.setParms({'grad_rad_on': rampData})
                    except:
                        message_stack.append('Cannot setting color_ramp...')
                        # ) end init ramp

                    for i in range(0, len(parm_val)):
                        parm_name = 'grad_rad_on' + str(i + 1) + 'pos'
                        pos = self.try_parse_parm_value(node_name, node_type, parm_name, parm_val[i], message_stack)
                        self.try_set_parm(node, parm_name, pos, message_stack)

                elif node_type == 'TexSoftbox' and parm_name == 'grad_rad_col':
                    # grad_rad_col = ['AColor(0', '1', '0.9882354', '1']

                    for i in range(0, len(parm_val)):
                        parm_name = 'grad_rad_on' + str(i + 1) + 'c'
                        c = self.try_parse_parm_value(node_name, node_type, parm_name, parm_val[i], message_stack)
                        c = hou.Vector3((c.x(), c.y(), c.z()))  # Vector4 to Vector3
                        self.try_set_parm(node, parm_name, c, message_stack)

                elif node_type == 'TexSoftbox' and parm_name == 'frame_pos':
                    # frame_col = ['0', '1']

                    # init ramp with default values (
                    count = len(parm_val)
                    rampData = hou.Ramp([hou.rampBasis.Linear] * count, [x * 1. / (count - 1) for x in range(0, count)],
                                        [(0.0, 0.0, 0.0)] * count)
                    try:
                        node.setParms({'frame_on': rampData})
                    except:
                        message_stack.append('Cannot setting color_ramp...')
                        # ) end init ramp

                    for i in range(0, len(parm_val)):
                        parm_name = 'frame_on' + str(i + 1) + 'pos'
                        pos = self.try_parse_parm_value(node_name, node_type, parm_name, parm_val[i], message_stack)
                        self.try_set_parm(node, parm_name, pos, message_stack)

                elif node_type == 'TexSoftbox' and parm_name == 'frame_col':
                    # frame_col = ['AColor(0', '1', '0.9882354', '1']

                    for i in range(0, len(parm_val)):
                        parm_name = 'frame_on' + str(i + 1) + 'c'
                        c = self.try_parse_parm_value(node_name, node_type, parm_name, parm_val[i], message_stack)
                        c = hou.Vector3((c.x(), c.y(), c.z()))  # Vector4 to Vector3
                        self.try_set_parm(node, parm_name, c, message_stack)


                elif '@' in str(parm_val) or 'bitmapBuffer' in str(parm_val):
                    for nn in plugins:
                        name = str(parm_val)
                        if '::' in name:
                            split = name.split('::')
                            name = split[0]
                            output_name = split[1]
                        if nn['Name'] == name:
                            self.add_plugin_node(plugins, parent, node, parm_name, nn['Name'], nn['Type'], nn['Parms'],
                                                 message_stack, output_name=output_name)

                else:

                    print parm_name + " = " + str(parm_val)
                    self.try_set_parm(node, parm_name, parm_val, message_stack)

    def load_materials(self, plugins, materials):
        # loading materials
        message_stack = list()
        shop = hou.node('/shop')

        print '\n\n\n#############################################'
        print '#########  LOADING SCENE MATERIALS  #########'
        print '#############################################\n\n'

        for m in materials:

            material = self.try_create_node(shop, 'vray_material', self.normalize_name(m['Name']), message_stack)

            if material != None:
                for child in material.children():
                    child.destroy()

                for n in plugins:
                    if n['Name'] == m['Codename']:
                        material_output = self.get_material_output(material)
                        input_name = 'Material'

                        self.add_plugin_node(plugins, material, material_output, input_name, n['Name'], n['Type'],
                                             n['Parms'],
                                             message_stack)

                        self.auto_arrange_children(material)

                        break

        self.auto_arrange_children(shop)

        if len(message_stack) != 0:
            print '\n\n\nLoad Scene materials terminated with: ' + str(len(message_stack)) + ' errors:\n'
        else:
            print '\n\n\nLoad Scene materials terminated successfully\n'

        for m in message_stack:
            print m

    def get_environment_settings(self, environment_rop):
        render_environment = None
        result = [child for child in environment_rop.children() if
                  child.type().name() == 'VRayNodeSettingsEnvironment']

        if len(result) > 0:
            render_environment = result[0]
        else:
            render_environment = environment_rop.createNode('VRayNodeSettingsEnvironment')
            render_environment.moveToGoodPosition()
        return render_environment

    def find_or_create_user_color(self, output_node, parent, input_name, parm_val, message_stack):
        node = None

        for child in parent.children():
            if child.type().name() == 'VRayNodeTexUserColor':
                if hou.Vector4(child.parmTuple('default_color').eval()) == parm_val:
                    node = child
                    break

        if node == None:
            node = parent.createNode('VRayNodeTexUserColor')

            count = 1
            while parent.node('usercolor_' + str(count)) != None: count += 1
            node.setName('usercolor_' + str(count))

            self.try_set_parm(node, 'default_color', parm_val, message_stack)

        self.try_set_input(output_node, input_name, node, message_stack)

    def load_environments(self, plugins, environments):
        # loading environment
        message_stack = list()

        vray_rop = self.get_vray_rop_node()
        env = hou.node(vray_rop.parm('render_network_environment').eval())

        if env == None:
            out = hou.node('/out')
            env = out.createNode('vray_environment', 'env')
            env.moveToGoodPosition()
            vray_rop.parm('render_network_environment').set(env.path())

        for child in env.children():
            if child.type().name() != 'VRayNodeSettingsEnvironment':
                child.destroy()

        output_node = self.get_environment_settings(env)

        print '\n\n\n#############################################'
        print '########  LOADING SCENE ENVIRONMENT  ########'
        print '#############################################\n\n'

        for p in environments:
            parm_name = p['Name']
            parm_val = self.try_parse_parm_value(output_node, 'SettingsEnvironment', parm_name, p['Value'],
                                                 message_stack)

            print parm_name + " = " + str(parm_val)

            if isinstance(parm_val, hou.Vector4):
                self.find_or_create_user_color(output_node, env, parm_name, parm_val, message_stack)

            for nn in plugins:
                if nn['Name'] == str(parm_val):
                    self.add_plugin_node(plugins, env, output_node, parm_name, nn['Name'], nn['Type'], nn['Parms'],
                                         message_stack)

            print '\n\n'

        self.auto_arrange_children(env)

        if len(message_stack) != 0:
            print '\n\n\nLoad Scene environment terminated with: ' + str(len(message_stack)) + ' errors:\n'
        else:
            print '\n\n\nLoad Scene environment terminated successfully\n'

        for m in message_stack:
            print m

    def format_elapsed_time(self, elapsed):
        if elapsed > 60 * 60:
            elapsed /= 60 * 60
            return str(float("{0:.2f}".format(elapsed))) + ' hours'
        elif elapsed > 60:
            elapsed /= 60
            return str(float("{0:.2f}".format(elapsed))) + ' minutes'
        else:
            return str(float("{0:.2f}".format(elapsed))) + ' seconds'

    def auto_arrange_children(self, node, fit=False):
        node.layoutChildren()
        self.network_tab.cd(node.path())
        for child in node.children():
            child.setSelected(True)
        self.network_tab.homeToSelection()
        for child in node.children():
            child.setSelected(False)

    def set_environment_variable(self, var, value):
        import os
        os.environ[var] = value
        try:
            hou.allowEnvironmentVariableToOverwriteVariable(var, True)
        except AttributeError:
            hou.allowEnvironmentToOverwriteVariable(var, True)

        hscript_command = "set %s = %s" % (var, value)
        hou.hscript(str(hscript_command))

    def run(self):
        import timeit
        import datetime
        import sys
        import hou

        clipboard = QtWidgets.QApplication.clipboard()
        text = clipboard.text()
        lines = text.splitlines()

        plugins = list()
        cameras = list()
        lights = list()
        settings = list()
        render_channels = list()
        nodes = list()
        materials = list()
        environments = list()
        geometries = list()
        target_objects = list()
        displacements = list()

        if lines.count > 1:
            if lines[0] == '#scene_export':

                last_hip_dir = hou.getenv('$HIP')
                hip_dir = hou.ui.selectFile(start_directory=last_hip_dir, title='Select project directory',
                                            file_type=hou.fileType.Directory)

                if hip_dir != '':
                    if hip_dir.endswith('/'):
                        hip_dir = hip_dir[:-1]  # remove last '/'

                    # self.set_environment_variable('JOB', hip_dir)
                    self.set_environment_variable('HIP', hip_dir)
                    self.set_environment_variable('HIPFILE', hip_dir + '/untitled.hip')
                else:
                    hip_dir = last_hip_dir

                print '\nScene import started...'

                start_time = timeit.default_timer()

                now = datetime.datetime.now()
                str_now = str(now.year) + '_' + str(now.month) + '_' + str(now.day) + '_' + str(now.hour) + '_' + str(
                    now.minute)

                log_filename = hip_dir + '/scene_import_' + str_now + '.log'
                log_file = open(log_filename, 'w')

                old_stdout = sys.stdout
                sys.stdout = log_file

                try:
                    for line in lines[1:]:
                        ls = line.split(',', 1)
                        if len(ls) == 2:
                            if ls[0] == 'filename':
                                self.parse_vrscene_file(ls[1], plugins, cameras, lights, settings, render_channels,
                                                        nodes,
                                                        environments, geometries, target_objects, displacements)

                                self.load_cameras(cameras, target_objects)
                                self.load_lights(lights, target_objects)
                                self.load_nodes(nodes, geometries, materials, displacements, plugins)
                                self.load_materials(plugins, materials)
                                self.load_environments(plugins, environments)
                                self.load_render_channels(plugins, render_channels)
                                self.load_settings(settings)

                    obj = hou.node('/obj')
                    self.network_tab.cd(obj.path())  # TEST
                    self.auto_arrange_children(obj, True)

                    print '\n\n\n#############################################'
                    print '###################  END  ###################'
                    print '#############################################'

                except:
                    sys.stdout = old_stdout
                    log_file.close()

                sys.stdout = old_stdout
                log_file.close()

                elapsed = timeit.default_timer() - start_time

                print '\n...scene import finished in ' + self.format_elapsed_time(elapsed)
                print '\nSee log file: ' + log_filename

            else:
                print '\nNothing to import !'


with hou.undos.group("Import Scene From Clipboard"):
    import_scene_from_clipboard().run()
