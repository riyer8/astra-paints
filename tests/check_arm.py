import mujoco
model = mujoco.MjModel.from_xml_path("sim/arm.xml")
for kind, n, label in [(mujoco.mjtObj.mjOBJ_BODY, model.nbody, "bodies"),
                       (mujoco.mjtObj.mjOBJ_JOINT, model.njnt, "joints"),
                       (mujoco.mjtObj.mjOBJ_ACTUATOR, model.nu, "actuators")]:
    names = [mujoco.mj_id2name(model, kind, i) for i in range(n)]
    print(label, ":", names)
