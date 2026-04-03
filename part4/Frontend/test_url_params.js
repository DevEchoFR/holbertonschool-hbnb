// Simulate browser environment
const testCases = [
  { url: 'create_edit_place.html?id=abc123', expectedId: 'abc123' },
  { url: 'create_edit_place.html?id=a9601b85-ba4c-4de6-ba0b-75d3f5aac7cd', expectedId: 'a9601b85-ba4c-4de6-ba0b-75d3f5aac7cd' },
  { url: 'create_edit_place.html?place_id=xyz789', expectedId: 'xyz789' },
  { url: 'create_edit_place.html', expectedId: '' },
  { url: 'create_edit_place.html?id=', expectedId: '' },
  { url: 'create_edit_place.html?id=undefined', expectedId: '' },
  { url: 'create_edit_place.html?id=null', expectedId: '' },
];

testCases.forEach(testCase => {
  // Test regex extraction
  const searchString = '?' + new URL('http://localhost' + testCase.url).search.substring(1);
  const exactMatch = searchString.match(/[?&]id=([^&]+)/);
  const extractedId = exactMatch ? decodeURIComponent(exactMatch[1]) : '';
  const finalId = (extractedId && extractedId !== 'undefined' && extractedId !== 'null' && extractedId !== '') ? extractedId : '';
  
  const passed = finalId === testCase.expectedId;
  console.log(`${passed ? '✓ PASS' : '✗ FAIL'}: ${testCase.url}`);
  console.log(`  Expected: "${testCase.expectedId}", Got: "${finalId}"`);
});
