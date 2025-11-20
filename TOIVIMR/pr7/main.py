import train_net
import numpy as np

#train_net.load_samples("detection_history.txt")
#train_net.train_net('weights.h5')


net = train_net.create_model(15, 15, 'weights.h5')

alphabet, _, _, _ = train_net.load_samples("detection_history.txt")

test="fir "

#TODO: найти способ преобразования размера массива inp
for ch in test:
    inp=train_net.encode_letter(ch, alphabet)
    inp = [inp]
    #out=net.predict(np.array([inp]))
    out=net.predict(np.array(inp))
    out_ch=train_net.decode_letter(out, alphabet)
    print(out_ch)

generated_text=""
out_ch="b"
for i in range(100):
    inp_ch=out_ch
    inp=train_net.encode_letter(inp_ch, alphabet)
    #out=net.predict(np.array([inp]))
    inp = [inp]
    out=net.predict(np.array(inp))

    out_ch=train_net.decode_letter(out, alphabet)
    generated_text+=out_ch

print(f"generated: {generated_text}")

