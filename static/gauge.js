/**
 * Updates the needle position of a gauge based on a given value.
 * @param {number} value - The value to display on the gauge.
 * @param {number} min - The minimum value of the gauge range.
 * @param {number} max - The maximum value of the gauge range.
 * @param {string} needleId - The ID of the needle element to update.
 * @param {string} valueId - The ID of the value element to update.
 */
function updateGauge(value, min, max, needleId, valueId, gaugeId) {
    const needle = document.getElementById(needleId);
    const valueDisplay = document.getElementById(valueId);
    const gauge = document.getElementById(gaugeId);

    if (!needle || !valueDisplay || !gauge) return;

    // Clamp the value to be within the min and max range
    const clampedValue = Math.min(Math.max(value, min), max);

    // Update the displayed value text
    valueDisplay.textContent = `${valueDisplay.dataset.label || 'Value'}: ${clampedValue}`;

    // Calculate the percentage of the value relative to the min and max range
    const percentage = (clampedValue - min) / (max - min); // Value between 0 and 1

    // Define the angle range (0° to 180°) for the gauge
    const maxAngle = 180;  // Maximum angle for the needle (e.g., 180 degrees)
    const minAngle = 0;    // Minimum angle (0 degrees for the starting position)

    // Calculate the rotation angle based on the percentage
    const rotationAngle = minAngle + (percentage * (maxAngle - minAngle)); // This gives us the angle for the needle

    // Ensure the rotation angle stays within the bounds
    const finalRotationAngle = Math.min(Math.max(rotationAngle, minAngle), maxAngle);

    // Set the needle's rotation
    needle.style.transform = `translateX(-50%) rotate(${finalRotationAngle}deg)`;

    // Update the background gradient based on the percentage
    let startColor, middleColor, endColor;
    if (percentage < 0.5) {
        // Green to Yellow (For lower half of the range)
        startColor = "green";
        middleColor = "yellow";
        endColor = "red";
    } else {
        // Yellow to Red (For upper half of the range)
        startColor = "yellow";
        middleColor = "red";
        endColor = "red";
    }

    // Smoothly adjust the gradient between green, yellow, and red
    gauge.style.backgroundImage = `linear-gradient(to right, ${startColor}, ${middleColor}, ${endColor})`;
}