import cv2
import numpy
import logging


logger = logging.getLogger('indi_allsky')


class IndiAllskySqm(object):

    def __init__(self, config, binning, mask=None):
        self.config = config
        self.binning = binning

        # both masks will be combined
        self._external_mask = mask
        self._sqm_mask = None


    def calculate(self, img, exposure, gain):
        logger.info('Exposure: %0.6f, gain: %d', exposure, gain)

        if isinstance(self._sqm_mask, type(None)):
            # This only needs to be done once if a mask is not provided
            self._generateSqmMask(img)


        if len(img.shape) == 2:
            # mono
            img_gray = img
        else:
            # color
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


        sqm_avg = cv2.mean(src=img_gray, mask=self._sqm_mask)[0]
        logger.info('Raw SQM average: %0.2f', sqm_avg)

        # offset the sqm based on the exposure and gain
        weighted_sqm_avg = (((self.config['CCD_EXPOSURE_MAX'] - exposure) / 10) + 1) * (sqm_avg * (((self.config['CCD_CONFIG']['NIGHT']['GAIN'] - gain) / 10) + 1))

        logger.info('Weighted SQM average: %0.2f', weighted_sqm_avg)

        return weighted_sqm_avg


    def _generateSqmMask(self, img):
        logger.info('Generating mask based on SQM_ROI')

        image_height, image_width = img.shape[:2]

        # create a black background
        mask = numpy.zeros((image_height, image_width), dtype=numpy.uint8)

        sqm_roi = self.config.get('SQM_ROI', [])

        try:
            x1 = int(sqm_roi[0] / self.binning)
            y1 = int(sqm_roi[1] / self.binning)
            x2 = int(sqm_roi[2] / self.binning)
            y2 = int(sqm_roi[3] / self.binning)
        except IndexError:
            logger.warning('Using central 20% ROI for SQM calculations')
            x1 = int((image_width / 2) - (image_width / 5))
            y1 = int((image_height / 2) - (image_height / 5))
            x2 = int((image_width / 2) + (image_width / 5))
            y2 = int((image_height / 2) + (image_height / 5))

        # The white area is what we keep
        cv2.rectangle(
            img=mask,
            pt1=(x1, y1),
            pt2=(x2, y2),
            color=(255),  # mono
            thickness=cv2.FILLED,
        )


        # combine masks in case there is overlapping regions
        if not isinstance(self._external_mask, type(None)):
            self._sqm_mask = cv2.bitwise_and(mask, mask, mask=self._external_mask)
            return


        self._sqm_mask = mask

