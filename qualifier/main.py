import zerorpc
from ssim import compute_ssim
from PIL import Image


class RPCServer(object):
    def qualify(self, image1_path, image2_path):
        print("Received %s  %s" % (image1_path, image2_path))

        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)
        score = compute_ssim(image1, image2, gaussian_kernel_sigma=1.5, gaussian_kernel_width=11)

        print "qualified", score
        return score


s = zerorpc.Server(RPCServer())
s.bind("tcp://0.0.0.0:4242")
print('Waiting for messages.')
s.run()
