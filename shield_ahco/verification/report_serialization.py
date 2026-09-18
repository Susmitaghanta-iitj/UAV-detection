from shield_ahco.cycle_model.layer_model import DenseLayer,SharedMacCycleModel,dense_serialization_reduction
m=SharedMacCycleModel()
b=m.dense_cycles("before",DenseLayer(35072,256))
a=m.dense_cycles("after",DenseLayer(8704,256))
print("before",b)
print("after ",a)
print("reduction",dense_serialization_reduction())
