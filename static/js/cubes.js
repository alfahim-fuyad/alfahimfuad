/* cubes.js — 3D Skill Cubes interaction.
 *
 * - Each cube auto-rotates (CSS animation).
 * - Hover → glow + pause rotation.
 * - Click or Enter/Space → flip the cube to show the back face
 *   (skill details). Click again or press Escape to flip back.
 * - Only one cube is flipped at a time.
 */
(function () {
  var cubes = document.querySelectorAll('.cube');
  if (!cubes.length) return;

  var flipped = null;

  function flip(cube) {
    if (flipped && flipped !== cube) {
      flipped.classList.remove('flipped');
    }
    if (cube.classList.contains('flipped')) {
      cube.classList.remove('flipped');
      flipped = null;
    } else {
      cube.classList.add('flipped');
      flipped = cube;
    }
  }

  cubes.forEach(function (cube) {
    cube.addEventListener('click', function () {
      flip(cube);
    });
    cube.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        flip(cube);
      }
    });
  });

  // Press Escape to unflip any flipped cube.
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && flipped) {
      flipped.classList.remove('flipped');
      flipped = null;
    }
  });
})();
