"""Adversarial input for the comment scanner.

Legal-ish Python chosen to make the lexer work hard while emitting few
reportable blocks: hash-heavy strings that are not comments, very long
lines whose trailing comments must be rejected, nested f-strings, mixed
line endings, non-ASCII text, and recoverable lexical errors followed by
real walls. The file ends on an unclosed bracket, which makes the lexer
repeat its EOF error forever unless the scanner stops on its own.
"""

# A wall that is not a wall: 120 hash-prefixed lines inside one string
# literal. The lexer has to scan every byte and emits a single token.
DOC = """
# line 000 of prose that starts with a hash but is string content
# line 001 of prose that starts with a hash but is string content
# line 002 of prose that starts with a hash but is string content
# line 003 of prose that starts with a hash but is string content
# line 004 of prose that starts with a hash but is string content
# line 005 of prose that starts with a hash but is string content
# line 006 of prose that starts with a hash but is string content
# line 007 of prose that starts with a hash but is string content
# line 008 of prose that starts with a hash but is string content
# line 009 of prose that starts with a hash but is string content
# line 010 of prose that starts with a hash but is string content
# line 011 of prose that starts with a hash but is string content
# line 012 of prose that starts with a hash but is string content
# line 013 of prose that starts with a hash but is string content
# line 014 of prose that starts with a hash but is string content
# line 015 of prose that starts with a hash but is string content
# line 016 of prose that starts with a hash but is string content
# line 017 of prose that starts with a hash but is string content
# line 018 of prose that starts with a hash but is string content
# line 019 of prose that starts with a hash but is string content
# line 020 of prose that starts with a hash but is string content
# line 021 of prose that starts with a hash but is string content
# line 022 of prose that starts with a hash but is string content
# line 023 of prose that starts with a hash but is string content
# line 024 of prose that starts with a hash but is string content
# line 025 of prose that starts with a hash but is string content
# line 026 of prose that starts with a hash but is string content
# line 027 of prose that starts with a hash but is string content
# line 028 of prose that starts with a hash but is string content
# line 029 of prose that starts with a hash but is string content
# line 030 of prose that starts with a hash but is string content
# line 031 of prose that starts with a hash but is string content
# line 032 of prose that starts with a hash but is string content
# line 033 of prose that starts with a hash but is string content
# line 034 of prose that starts with a hash but is string content
# line 035 of prose that starts with a hash but is string content
# line 036 of prose that starts with a hash but is string content
# line 037 of prose that starts with a hash but is string content
# line 038 of prose that starts with a hash but is string content
# line 039 of prose that starts with a hash but is string content
# line 040 of prose that starts with a hash but is string content
# line 041 of prose that starts with a hash but is string content
# line 042 of prose that starts with a hash but is string content
# line 043 of prose that starts with a hash but is string content
# line 044 of prose that starts with a hash but is string content
# line 045 of prose that starts with a hash but is string content
# line 046 of prose that starts with a hash but is string content
# line 047 of prose that starts with a hash but is string content
# line 048 of prose that starts with a hash but is string content
# line 049 of prose that starts with a hash but is string content
# line 050 of prose that starts with a hash but is string content
# line 051 of prose that starts with a hash but is string content
# line 052 of prose that starts with a hash but is string content
# line 053 of prose that starts with a hash but is string content
# line 054 of prose that starts with a hash but is string content
# line 055 of prose that starts with a hash but is string content
# line 056 of prose that starts with a hash but is string content
# line 057 of prose that starts with a hash but is string content
# line 058 of prose that starts with a hash but is string content
# line 059 of prose that starts with a hash but is string content
# line 060 of prose that starts with a hash but is string content
# line 061 of prose that starts with a hash but is string content
# line 062 of prose that starts with a hash but is string content
# line 063 of prose that starts with a hash but is string content
# line 064 of prose that starts with a hash but is string content
# line 065 of prose that starts with a hash but is string content
# line 066 of prose that starts with a hash but is string content
# line 067 of prose that starts with a hash but is string content
# line 068 of prose that starts with a hash but is string content
# line 069 of prose that starts with a hash but is string content
# line 070 of prose that starts with a hash but is string content
# line 071 of prose that starts with a hash but is string content
# line 072 of prose that starts with a hash but is string content
# line 073 of prose that starts with a hash but is string content
# line 074 of prose that starts with a hash but is string content
# line 075 of prose that starts with a hash but is string content
# line 076 of prose that starts with a hash but is string content
# line 077 of prose that starts with a hash but is string content
# line 078 of prose that starts with a hash but is string content
# line 079 of prose that starts with a hash but is string content
# line 080 of prose that starts with a hash but is string content
# line 081 of prose that starts with a hash but is string content
# line 082 of prose that starts with a hash but is string content
# line 083 of prose that starts with a hash but is string content
# line 084 of prose that starts with a hash but is string content
# line 085 of prose that starts with a hash but is string content
# line 086 of prose that starts with a hash but is string content
# line 087 of prose that starts with a hash but is string content
# line 088 of prose that starts with a hash but is string content
# line 089 of prose that starts with a hash but is string content
# line 090 of prose that starts with a hash but is string content
# line 091 of prose that starts with a hash but is string content
# line 092 of prose that starts with a hash but is string content
# line 093 of prose that starts with a hash but is string content
# line 094 of prose that starts with a hash but is string content
# line 095 of prose that starts with a hash but is string content
# line 096 of prose that starts with a hash but is string content
# line 097 of prose that starts with a hash but is string content
# line 098 of prose that starts with a hash but is string content
# line 099 of prose that starts with a hash but is string content
# line 100 of prose that starts with a hash but is string content
# line 101 of prose that starts with a hash but is string content
# line 102 of prose that starts with a hash but is string content
# line 103 of prose that starts with a hash but is string content
# line 104 of prose that starts with a hash but is string content
# line 105 of prose that starts with a hash but is string content
# line 106 of prose that starts with a hash but is string content
# line 107 of prose that starts with a hash but is string content
# line 108 of prose that starts with a hash but is string content
# line 109 of prose that starts with a hash but is string content
# line 110 of prose that starts with a hash but is string content
# line 111 of prose that starts with a hash but is string content
# line 112 of prose that starts with a hash but is string content
# line 113 of prose that starts with a hash but is string content
# line 114 of prose that starts with a hash but is string content
# line 115 of prose that starts with a hash but is string content
# line 116 of prose that starts with a hash but is string content
# line 117 of prose that starts with a hash but is string content
# line 118 of prose that starts with a hash but is string content
# line 119 of prose that starts with a hash but is string content
"""

# Twelve lines of a few hundred numeric literals each, every one closed by
# a trailing comment. Trailing comments never start a run, so each is
# located, measured against its line prefix and discarded.
ROW_00 = (0, 31, 62, 93, 124, 155, 186, 217, 248, 279, 310, 341, 372, 403, 434, 465, 496, 527, 558, 589, 620, 651, 682, 713, 744, 775, 806, 837, 868, 899, 930, 961, 992, 1023, 1054, 1085, 1116, 1147, 1178, 1209, 1240, 1271, 1302, 1333, 1364, 1395, 1426, 1457, 1488, 1519, 1550, 1581, 1612, 1643, 1674, 1705, 1736, 1767, 1798, 1829, 1860, 1891, 1922, 1953, 1984, 2015, 2046, 2077, 2108, 2139, 2170, 2201, 2232, 2263, 2294, 2325, 2356, 2387, 2418, 2449, 2480, 2511, 2542, 2573, 2604, 2635, 2666, 2697, 2728, 2759, 2790, 2821, 2852, 2883, 2914, 2945, 2976, 3007, 3038, 3069, 3100, 3131, 3162, 3193, 3224, 3255, 3286, 3317, 3348, 3379, 3410, 3441, 3472, 3503, 3534, 3565, 3596, 3627, 3658, 3689, 3720, 3751, 3782, 3813, 3844, 3875, 3906, 3937, 3968, 3999, 4030, 4061, 4092, 4123, 4154, 4185, 4216, 4247, 4278, 4309, 4340, 4371, 4402, 4433, 4464, 4495, 4526, 4557, 4588, 4619, 4650, 4681, 4712, 4743, 4774, 4805, 4836, 4867, 4898, 4929, 4960, 4991, 5022, 5053, 5084, 5115, 5146, 5177, 5208, 5239, 5270, 5301, 5332, 5363, 5394, 5425, 5456, 5487, 5518, 5549, 5580, 5611, 5642, 5673, 5704, 5735, 5766, 5797, 5828, 5859, 5890, 5921, 5952, 5983, 6014, 6045, 6076, 6107, 6138, 6169,)  # row 0, 200 literals, trailing only
ROW_01 = (977, 1008, 1039, 1070, 1101, 1132, 1163, 1194, 1225, 1256, 1287, 1318, 1349, 1380, 1411, 1442, 1473, 1504, 1535, 1566, 1597, 1628, 1659, 1690, 1721, 1752, 1783, 1814, 1845, 1876, 1907, 1938, 1969, 2000, 2031, 2062, 2093, 2124, 2155, 2186, 2217, 2248, 2279, 2310, 2341, 2372, 2403, 2434, 2465, 2496, 2527, 2558, 2589, 2620, 2651, 2682, 2713, 2744, 2775, 2806, 2837, 2868, 2899, 2930, 2961, 2992, 3023, 3054, 3085, 3116, 3147, 3178, 3209, 3240, 3271, 3302, 3333, 3364, 3395, 3426, 3457, 3488, 3519, 3550, 3581, 3612, 3643, 3674, 3705, 3736, 3767, 3798, 3829, 3860, 3891, 3922, 3953, 3984, 4015, 4046, 4077, 4108, 4139, 4170, 4201, 4232, 4263, 4294, 4325, 4356, 4387, 4418, 4449, 4480, 4511, 4542, 4573, 4604, 4635, 4666, 4697, 4728, 4759, 4790, 4821, 4852, 4883, 4914, 4945, 4976, 5007, 5038, 5069, 5100, 5131, 5162, 5193, 5224, 5255, 5286, 5317, 5348, 5379, 5410, 5441, 5472, 5503, 5534, 5565, 5596, 5627, 5658, 5689, 5720, 5751, 5782, 5813, 5844, 5875, 5906, 5937, 5968, 5999, 6030, 6061, 6092, 6123, 6154, 6185, 6216, 6247, 6278, 6309, 6340, 6371, 6402, 6433, 6464, 6495, 6526, 6557, 6588, 6619, 6650, 6681, 6712, 6743, 6774, 6805, 6836, 6867, 6898, 6929, 6960, 6991, 7022, 7053, 7084, 7115, 7146,)  # row 1, 200 literals, trailing only
ROW_02 = (1954, 1985, 2016, 2047, 2078, 2109, 2140, 2171, 2202, 2233, 2264, 2295, 2326, 2357, 2388, 2419, 2450, 2481, 2512, 2543, 2574, 2605, 2636, 2667, 2698, 2729, 2760, 2791, 2822, 2853, 2884, 2915, 2946, 2977, 3008, 3039, 3070, 3101, 3132, 3163, 3194, 3225, 3256, 3287, 3318, 3349, 3380, 3411, 3442, 3473, 3504, 3535, 3566, 3597, 3628, 3659, 3690, 3721, 3752, 3783, 3814, 3845, 3876, 3907, 3938, 3969, 4000, 4031, 4062, 4093, 4124, 4155, 4186, 4217, 4248, 4279, 4310, 4341, 4372, 4403, 4434, 4465, 4496, 4527, 4558, 4589, 4620, 4651, 4682, 4713, 4744, 4775, 4806, 4837, 4868, 4899, 4930, 4961, 4992, 5023, 5054, 5085, 5116, 5147, 5178, 5209, 5240, 5271, 5302, 5333, 5364, 5395, 5426, 5457, 5488, 5519, 5550, 5581, 5612, 5643, 5674, 5705, 5736, 5767, 5798, 5829, 5860, 5891, 5922, 5953, 5984, 6015, 6046, 6077, 6108, 6139, 6170, 6201, 6232, 6263, 6294, 6325, 6356, 6387, 6418, 6449, 6480, 6511, 6542, 6573, 6604, 6635, 6666, 6697, 6728, 6759, 6790, 6821, 6852, 6883, 6914, 6945, 6976, 7007, 7038, 7069, 7100, 7131, 7162, 7193, 7224, 7255, 7286, 7317, 7348, 7379, 7410, 7441, 7472, 7503, 7534, 7565, 7596, 7627, 7658, 7689, 7720, 7751, 7782, 7813, 7844, 7875, 7906, 7937, 7968, 7999, 8030, 8061, 8092, 8123,)  # row 2, 200 literals, trailing only
ROW_03 = (2931, 2962, 2993, 3024, 3055, 3086, 3117, 3148, 3179, 3210, 3241, 3272, 3303, 3334, 3365, 3396, 3427, 3458, 3489, 3520, 3551, 3582, 3613, 3644, 3675, 3706, 3737, 3768, 3799, 3830, 3861, 3892, 3923, 3954, 3985, 4016, 4047, 4078, 4109, 4140, 4171, 4202, 4233, 4264, 4295, 4326, 4357, 4388, 4419, 4450, 4481, 4512, 4543, 4574, 4605, 4636, 4667, 4698, 4729, 4760, 4791, 4822, 4853, 4884, 4915, 4946, 4977, 5008, 5039, 5070, 5101, 5132, 5163, 5194, 5225, 5256, 5287, 5318, 5349, 5380, 5411, 5442, 5473, 5504, 5535, 5566, 5597, 5628, 5659, 5690, 5721, 5752, 5783, 5814, 5845, 5876, 5907, 5938, 5969, 6000, 6031, 6062, 6093, 6124, 6155, 6186, 6217, 6248, 6279, 6310, 6341, 6372, 6403, 6434, 6465, 6496, 6527, 6558, 6589, 6620, 6651, 6682, 6713, 6744, 6775, 6806, 6837, 6868, 6899, 6930, 6961, 6992, 7023, 7054, 7085, 7116, 7147, 7178, 7209, 7240, 7271, 7302, 7333, 7364, 7395, 7426, 7457, 7488, 7519, 7550, 7581, 7612, 7643, 7674, 7705, 7736, 7767, 7798, 7829, 7860, 7891, 7922, 7953, 7984, 8015, 8046, 8077, 8108, 8139, 8170, 8201, 8232, 8263, 8294, 8325, 8356, 8387, 8418, 8449, 8480, 8511, 8542, 8573, 8604, 8635, 8666, 8697, 8728, 8759, 8790, 8821, 8852, 8883, 8914, 8945, 8976, 9007, 9038, 9069, 9100,)  # row 3, 200 literals, trailing only
ROW_04 = (3908, 3939, 3970, 4001, 4032, 4063, 4094, 4125, 4156, 4187, 4218, 4249, 4280, 4311, 4342, 4373, 4404, 4435, 4466, 4497, 4528, 4559, 4590, 4621, 4652, 4683, 4714, 4745, 4776, 4807, 4838, 4869, 4900, 4931, 4962, 4993, 5024, 5055, 5086, 5117, 5148, 5179, 5210, 5241, 5272, 5303, 5334, 5365, 5396, 5427, 5458, 5489, 5520, 5551, 5582, 5613, 5644, 5675, 5706, 5737, 5768, 5799, 5830, 5861, 5892, 5923, 5954, 5985, 6016, 6047, 6078, 6109, 6140, 6171, 6202, 6233, 6264, 6295, 6326, 6357, 6388, 6419, 6450, 6481, 6512, 6543, 6574, 6605, 6636, 6667, 6698, 6729, 6760, 6791, 6822, 6853, 6884, 6915, 6946, 6977, 7008, 7039, 7070, 7101, 7132, 7163, 7194, 7225, 7256, 7287, 7318, 7349, 7380, 7411, 7442, 7473, 7504, 7535, 7566, 7597, 7628, 7659, 7690, 7721, 7752, 7783, 7814, 7845, 7876, 7907, 7938, 7969, 8000, 8031, 8062, 8093, 8124, 8155, 8186, 8217, 8248, 8279, 8310, 8341, 8372, 8403, 8434, 8465, 8496, 8527, 8558, 8589, 8620, 8651, 8682, 8713, 8744, 8775, 8806, 8837, 8868, 8899, 8930, 8961, 8992, 9023, 9054, 9085, 9116, 9147, 9178, 9209, 9240, 9271, 9302, 9333, 9364, 9395, 9426, 9457, 9488, 9519, 9550, 9581, 9612, 9643, 9674, 9705, 9736, 9767, 9798, 9829, 9860, 9891, 9922, 9953, 11, 42, 73, 104,)  # row 4, 200 literals, trailing only
ROW_05 = (4885, 4916, 4947, 4978, 5009, 5040, 5071, 5102, 5133, 5164, 5195, 5226, 5257, 5288, 5319, 5350, 5381, 5412, 5443, 5474, 5505, 5536, 5567, 5598, 5629, 5660, 5691, 5722, 5753, 5784, 5815, 5846, 5877, 5908, 5939, 5970, 6001, 6032, 6063, 6094, 6125, 6156, 6187, 6218, 6249, 6280, 6311, 6342, 6373, 6404, 6435, 6466, 6497, 6528, 6559, 6590, 6621, 6652, 6683, 6714, 6745, 6776, 6807, 6838, 6869, 6900, 6931, 6962, 6993, 7024, 7055, 7086, 7117, 7148, 7179, 7210, 7241, 7272, 7303, 7334, 7365, 7396, 7427, 7458, 7489, 7520, 7551, 7582, 7613, 7644, 7675, 7706, 7737, 7768, 7799, 7830, 7861, 7892, 7923, 7954, 7985, 8016, 8047, 8078, 8109, 8140, 8171, 8202, 8233, 8264, 8295, 8326, 8357, 8388, 8419, 8450, 8481, 8512, 8543, 8574, 8605, 8636, 8667, 8698, 8729, 8760, 8791, 8822, 8853, 8884, 8915, 8946, 8977, 9008, 9039, 9070, 9101, 9132, 9163, 9194, 9225, 9256, 9287, 9318, 9349, 9380, 9411, 9442, 9473, 9504, 9535, 9566, 9597, 9628, 9659, 9690, 9721, 9752, 9783, 9814, 9845, 9876, 9907, 9938, 9969, 27, 58, 89, 120, 151, 182, 213, 244, 275, 306, 337, 368, 399, 430, 461, 492, 523, 554, 585, 616, 647, 678, 709, 740, 771, 802, 833, 864, 895, 926, 957, 988, 1019, 1050, 1081,)  # row 5, 200 literals, trailing only
ROW_06 = (5862, 5893, 5924, 5955, 5986, 6017, 6048, 6079, 6110, 6141, 6172, 6203, 6234, 6265, 6296, 6327, 6358, 6389, 6420, 6451, 6482, 6513, 6544, 6575, 6606, 6637, 6668, 6699, 6730, 6761, 6792, 6823, 6854, 6885, 6916, 6947, 6978, 7009, 7040, 7071, 7102, 7133, 7164, 7195, 7226, 7257, 7288, 7319, 7350, 7381, 7412, 7443, 7474, 7505, 7536, 7567, 7598, 7629, 7660, 7691, 7722, 7753, 7784, 7815, 7846, 7877, 7908, 7939, 7970, 8001, 8032, 8063, 8094, 8125, 8156, 8187, 8218, 8249, 8280, 8311, 8342, 8373, 8404, 8435, 8466, 8497, 8528, 8559, 8590, 8621, 8652, 8683, 8714, 8745, 8776, 8807, 8838, 8869, 8900, 8931, 8962, 8993, 9024, 9055, 9086, 9117, 9148, 9179, 9210, 9241, 9272, 9303, 9334, 9365, 9396, 9427, 9458, 9489, 9520, 9551, 9582, 9613, 9644, 9675, 9706, 9737, 9768, 9799, 9830, 9861, 9892, 9923, 9954, 12, 43, 74, 105, 136, 167, 198, 229, 260, 291, 322, 353, 384, 415, 446, 477, 508, 539, 570, 601, 632, 663, 694, 725, 756, 787, 818, 849, 880, 911, 942, 973, 1004, 1035, 1066, 1097, 1128, 1159, 1190, 1221, 1252, 1283, 1314, 1345, 1376, 1407, 1438, 1469, 1500, 1531, 1562, 1593, 1624, 1655, 1686, 1717, 1748, 1779, 1810, 1841, 1872, 1903, 1934, 1965, 1996, 2027, 2058,)  # row 6, 200 literals, trailing only
ROW_07 = (6839, 6870, 6901, 6932, 6963, 6994, 7025, 7056, 7087, 7118, 7149, 7180, 7211, 7242, 7273, 7304, 7335, 7366, 7397, 7428, 7459, 7490, 7521, 7552, 7583, 7614, 7645, 7676, 7707, 7738, 7769, 7800, 7831, 7862, 7893, 7924, 7955, 7986, 8017, 8048, 8079, 8110, 8141, 8172, 8203, 8234, 8265, 8296, 8327, 8358, 8389, 8420, 8451, 8482, 8513, 8544, 8575, 8606, 8637, 8668, 8699, 8730, 8761, 8792, 8823, 8854, 8885, 8916, 8947, 8978, 9009, 9040, 9071, 9102, 9133, 9164, 9195, 9226, 9257, 9288, 9319, 9350, 9381, 9412, 9443, 9474, 9505, 9536, 9567, 9598, 9629, 9660, 9691, 9722, 9753, 9784, 9815, 9846, 9877, 9908, 9939, 9970, 28, 59, 90, 121, 152, 183, 214, 245, 276, 307, 338, 369, 400, 431, 462, 493, 524, 555, 586, 617, 648, 679, 710, 741, 772, 803, 834, 865, 896, 927, 958, 989, 1020, 1051, 1082, 1113, 1144, 1175, 1206, 1237, 1268, 1299, 1330, 1361, 1392, 1423, 1454, 1485, 1516, 1547, 1578, 1609, 1640, 1671, 1702, 1733, 1764, 1795, 1826, 1857, 1888, 1919, 1950, 1981, 2012, 2043, 2074, 2105, 2136, 2167, 2198, 2229, 2260, 2291, 2322, 2353, 2384, 2415, 2446, 2477, 2508, 2539, 2570, 2601, 2632, 2663, 2694, 2725, 2756, 2787, 2818, 2849, 2880, 2911, 2942, 2973, 3004, 3035,)  # row 7, 200 literals, trailing only
ROW_08 = (7816, 7847, 7878, 7909, 7940, 7971, 8002, 8033, 8064, 8095, 8126, 8157, 8188, 8219, 8250, 8281, 8312, 8343, 8374, 8405, 8436, 8467, 8498, 8529, 8560, 8591, 8622, 8653, 8684, 8715, 8746, 8777, 8808, 8839, 8870, 8901, 8932, 8963, 8994, 9025, 9056, 9087, 9118, 9149, 9180, 9211, 9242, 9273, 9304, 9335, 9366, 9397, 9428, 9459, 9490, 9521, 9552, 9583, 9614, 9645, 9676, 9707, 9738, 9769, 9800, 9831, 9862, 9893, 9924, 9955, 13, 44, 75, 106, 137, 168, 199, 230, 261, 292, 323, 354, 385, 416, 447, 478, 509, 540, 571, 602, 633, 664, 695, 726, 757, 788, 819, 850, 881, 912, 943, 974, 1005, 1036, 1067, 1098, 1129, 1160, 1191, 1222, 1253, 1284, 1315, 1346, 1377, 1408, 1439, 1470, 1501, 1532, 1563, 1594, 1625, 1656, 1687, 1718, 1749, 1780, 1811, 1842, 1873, 1904, 1935, 1966, 1997, 2028, 2059, 2090, 2121, 2152, 2183, 2214, 2245, 2276, 2307, 2338, 2369, 2400, 2431, 2462, 2493, 2524, 2555, 2586, 2617, 2648, 2679, 2710, 2741, 2772, 2803, 2834, 2865, 2896, 2927, 2958, 2989, 3020, 3051, 3082, 3113, 3144, 3175, 3206, 3237, 3268, 3299, 3330, 3361, 3392, 3423, 3454, 3485, 3516, 3547, 3578, 3609, 3640, 3671, 3702, 3733, 3764, 3795, 3826, 3857, 3888, 3919, 3950, 3981, 4012,)  # row 8, 200 literals, trailing only
ROW_09 = (8793, 8824, 8855, 8886, 8917, 8948, 8979, 9010, 9041, 9072, 9103, 9134, 9165, 9196, 9227, 9258, 9289, 9320, 9351, 9382, 9413, 9444, 9475, 9506, 9537, 9568, 9599, 9630, 9661, 9692, 9723, 9754, 9785, 9816, 9847, 9878, 9909, 9940, 9971, 29, 60, 91, 122, 153, 184, 215, 246, 277, 308, 339, 370, 401, 432, 463, 494, 525, 556, 587, 618, 649, 680, 711, 742, 773, 804, 835, 866, 897, 928, 959, 990, 1021, 1052, 1083, 1114, 1145, 1176, 1207, 1238, 1269, 1300, 1331, 1362, 1393, 1424, 1455, 1486, 1517, 1548, 1579, 1610, 1641, 1672, 1703, 1734, 1765, 1796, 1827, 1858, 1889, 1920, 1951, 1982, 2013, 2044, 2075, 2106, 2137, 2168, 2199, 2230, 2261, 2292, 2323, 2354, 2385, 2416, 2447, 2478, 2509, 2540, 2571, 2602, 2633, 2664, 2695, 2726, 2757, 2788, 2819, 2850, 2881, 2912, 2943, 2974, 3005, 3036, 3067, 3098, 3129, 3160, 3191, 3222, 3253, 3284, 3315, 3346, 3377, 3408, 3439, 3470, 3501, 3532, 3563, 3594, 3625, 3656, 3687, 3718, 3749, 3780, 3811, 3842, 3873, 3904, 3935, 3966, 3997, 4028, 4059, 4090, 4121, 4152, 4183, 4214, 4245, 4276, 4307, 4338, 4369, 4400, 4431, 4462, 4493, 4524, 4555, 4586, 4617, 4648, 4679, 4710, 4741, 4772, 4803, 4834, 4865, 4896, 4927, 4958, 4989,)  # row 9, 200 literals, trailing only
ROW_10 = (9770, 9801, 9832, 9863, 9894, 9925, 9956, 14, 45, 76, 107, 138, 169, 200, 231, 262, 293, 324, 355, 386, 417, 448, 479, 510, 541, 572, 603, 634, 665, 696, 727, 758, 789, 820, 851, 882, 913, 944, 975, 1006, 1037, 1068, 1099, 1130, 1161, 1192, 1223, 1254, 1285, 1316, 1347, 1378, 1409, 1440, 1471, 1502, 1533, 1564, 1595, 1626, 1657, 1688, 1719, 1750, 1781, 1812, 1843, 1874, 1905, 1936, 1967, 1998, 2029, 2060, 2091, 2122, 2153, 2184, 2215, 2246, 2277, 2308, 2339, 2370, 2401, 2432, 2463, 2494, 2525, 2556, 2587, 2618, 2649, 2680, 2711, 2742, 2773, 2804, 2835, 2866, 2897, 2928, 2959, 2990, 3021, 3052, 3083, 3114, 3145, 3176, 3207, 3238, 3269, 3300, 3331, 3362, 3393, 3424, 3455, 3486, 3517, 3548, 3579, 3610, 3641, 3672, 3703, 3734, 3765, 3796, 3827, 3858, 3889, 3920, 3951, 3982, 4013, 4044, 4075, 4106, 4137, 4168, 4199, 4230, 4261, 4292, 4323, 4354, 4385, 4416, 4447, 4478, 4509, 4540, 4571, 4602, 4633, 4664, 4695, 4726, 4757, 4788, 4819, 4850, 4881, 4912, 4943, 4974, 5005, 5036, 5067, 5098, 5129, 5160, 5191, 5222, 5253, 5284, 5315, 5346, 5377, 5408, 5439, 5470, 5501, 5532, 5563, 5594, 5625, 5656, 5687, 5718, 5749, 5780, 5811, 5842, 5873, 5904, 5935, 5966,)  # row 10, 200 literals, trailing only
ROW_11 = (774, 805, 836, 867, 898, 929, 960, 991, 1022, 1053, 1084, 1115, 1146, 1177, 1208, 1239, 1270, 1301, 1332, 1363, 1394, 1425, 1456, 1487, 1518, 1549, 1580, 1611, 1642, 1673, 1704, 1735, 1766, 1797, 1828, 1859, 1890, 1921, 1952, 1983, 2014, 2045, 2076, 2107, 2138, 2169, 2200, 2231, 2262, 2293, 2324, 2355, 2386, 2417, 2448, 2479, 2510, 2541, 2572, 2603, 2634, 2665, 2696, 2727, 2758, 2789, 2820, 2851, 2882, 2913, 2944, 2975, 3006, 3037, 3068, 3099, 3130, 3161, 3192, 3223, 3254, 3285, 3316, 3347, 3378, 3409, 3440, 3471, 3502, 3533, 3564, 3595, 3626, 3657, 3688, 3719, 3750, 3781, 3812, 3843, 3874, 3905, 3936, 3967, 3998, 4029, 4060, 4091, 4122, 4153, 4184, 4215, 4246, 4277, 4308, 4339, 4370, 4401, 4432, 4463, 4494, 4525, 4556, 4587, 4618, 4649, 4680, 4711, 4742, 4773, 4804, 4835, 4866, 4897, 4928, 4959, 4990, 5021, 5052, 5083, 5114, 5145, 5176, 5207, 5238, 5269, 5300, 5331, 5362, 5393, 5424, 5455, 5486, 5517, 5548, 5579, 5610, 5641, 5672, 5703, 5734, 5765, 5796, 5827, 5858, 5889, 5920, 5951, 5982, 6013, 6044, 6075, 6106, 6137, 6168, 6199, 6230, 6261, 6292, 6323, 6354, 6385, 6416, 6447, 6478, 6509, 6540, 6571, 6602, 6633, 6664, 6695, 6726, 6757, 6788, 6819, 6850, 6881, 6912, 6943,)  # row 11, 200 literals, trailing only

# Nested f-strings with hashes inside the replacement fields.
DEPTH = 3
NEST = f"{f'{DEPTH}#{DEPTH}'}#{f'{DEPTH:>#5}'}"
ALSO = f'#{NEST}#' f"{'#' * DEPTH}"
RAW = rb'# not a comment either \x00'

# Stray closing bracket below: the lexer reports it and resynchronises, so
# the wall after it still has to be found.
BAD = 1)
# recovery wall A line 0
# recovery wall A line 1
# recovery wall A line 2
# recovery wall A line 3
# recovery wall A line 4
# recovery wall A line 5
# recovery wall A line 6
# recovery wall A line 7

STILL = 2

# Non-ASCII identifiers, string content and comments: byte offsets and
# character columns diverge for everything below this point.
описание = "аргумент со знаком # внутри"  # хвостовой комментарий
# строка стены номер 0
# строка стены номер 1
# строка стены номер 2
# строка стены номер 3
# строка стены номер 4
# строка стены номер 5
# строка стены номер 6
# строка стены номер 7

# Mixed tabs and spaces inside a suite: another recoverable lexical error.
if STILL:
 	# indented wall line 0
	 # indented wall line 1
 	# indented wall line 2
	 # indented wall line 3
 	# indented wall line 4
	 # indented wall line 5
 	# indented wall line 6
	 # indented wall line 7
	pass

# Windows line endings from here to the tail: the carriage returns must
# not be counted as extra lines.
CRLF = 1
# crlf wall line 0
# crlf wall line 1
# crlf wall line 2
# crlf wall line 3
# crlf wall line 4
# crlf wall line 5
# crlf wall line 6
# crlf wall line 7
CRLF += 1

# The file ends inside an unclosed call. The lexer repeats its EOF error
# for as long as it is polled, so the scanner has to stop on the first
# repeat -- and this wall, which precedes the bracket, still counts.
UNCLOSED = max(
